#!/usr/bin/env python3
"""Build a source-by-source nationality research manifest for every blank row.

This script is read-only with respect to data/*.csv. It retrieves Wikipedia /
Wikidata and TheSmackDownHotel profile evidence, then writes a review manifest.
Database application is deliberately a separate guarded step.
"""

from __future__ import annotations

import csv
import html
import json
import re
import time
import unicodedata
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUT = ROOT / "research" / "nationality_sweep_20260928.csv"
UA = "RoyalRumbleStatisticsDatabase/1.0 (research; contact via project owner)"


COUNTRY_TO_DEMONYM = {
    "United States of America": "American", "United States": "American",
    "Canada": "Canadian", "England": "English", "Scotland": "Scottish",
    "Wales": "Welsh", "Northern Ireland": "Northern Irish",
    "United Kingdom": "British", "Ireland": "Irish", "Republic of Ireland": "Irish",
    "Mexico": "Mexican", "Puerto Rico": "Puerto Rican", "Cuba": "Cuban",
    "Dominican Republic": "Dominican", "Haiti": "Haitian", "Jamaica": "Jamaican",
    "Trinidad and Tobago": "Trinidadian", "Brazil": "Brazilian",
    "Argentina": "Argentine", "Chile": "Chilean", "Colombia": "Colombian",
    "Guyana": "Guyanese", "Italy": "Italian", "France": "French",
    "Germany": "German", "Austria": "Austrian", "Switzerland": "Swiss",
    "Netherlands": "Dutch", "Belgium": "Belgian", "Spain": "Spanish",
    "Portugal": "Portuguese", "Greece": "Greek", "Poland": "Polish",
    "Russia": "Russian", "Soviet Union": "Soviet", "Ukraine": "Ukrainian",
    "Bulgaria": "Bulgarian", "Romania": "Romanian", "Croatia": "Croatian",
    "Serbia": "Serbian", "Finland": "Finnish", "Sweden": "Swedish",
    "Norway": "Norwegian", "Denmark": "Danish", "Iceland": "Icelandic",
    "Australia": "Australian", "New Zealand": "New Zealander", "Fiji": "Fijian",
    "Samoa": "Samoan", "Tonga": "Tongan", "Japan": "Japanese",
    "China": "Chinese", "People's Republic of China": "Chinese",
    "Taiwan": "Taiwanese", "South Korea": "South Korean", "India": "Indian",
    "Pakistan": "Pakistani", "Iran": "Iranian", "Iraq": "Iraqi",
    "Saudi Arabia": "Saudi Arabian", "Israel": "Israeli", "Turkey": "Turkish",
    "South Africa": "South African", "Nigeria": "Nigerian", "Ghana": "Ghanaian",
    "Uganda": "Ugandan", "Cameroon": "Cameroonian", "Egypt": "Egyptian",
}


def fetch(url: str, timeout: int = 30) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "en"})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return response.read()


def api(base: str, params: dict) -> dict:
    query = urllib.parse.urlencode(params)
    return json.loads(fetch(f"{base}?{query}").decode("utf-8"))


def norm(value: str) -> str:
    value = unicodedata.normalize("NFKD", value or "").encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "", value.lower())


def clean_text(value: str) -> str:
    value = re.sub(r"<[^>]+>", " ", value)
    return re.sub(r"\s+", " ", html.unescape(value)).strip()


def load_sdh_profiles() -> list[str]:
    root = ET.fromstring(fetch("https://www.thesmackdownhotel.com/sitemap.xml"))
    sitemap_urls = [node.text for node in root.findall("{*}sitemap/{*}loc") if node.text]
    profiles = []
    for sitemap_url in sitemap_urls:
        tree = ET.fromstring(fetch(sitemap_url))
        profiles.extend(
            node.text for node in tree.findall("{*}url/{*}loc")
            if node.text and "/wrestlers/" in node.text
        )
    return sorted(set(profiles))


def sdh_candidate(row: dict, profiles: list[str]) -> str:
    keys = {norm(row["wrestler_id"]), norm(row["ring_name"]), norm(row["real_name"])} - {""}
    exact = []
    broad = []
    for url in profiles:
        slug = url.rstrip("/").rsplit("/", 1)[-1]
        slug_norm = norm(slug)
        if slug_norm in keys:
            exact.append(url)
        elif any(len(key) >= 5 and (slug_norm.startswith(key) or key.startswith(slug_norm)) for key in keys):
            broad.append(url)
    candidates = exact or broad
    return candidates[0] if len(candidates) == 1 else ""


def parse_sdh(url: str) -> str:
    if not url:
        return ""
    text = fetch(url).decode("utf-8", "ignore")
    patterns = [
        r'alt=["\']Nationality:\s*([^"\']+)',
        r'Nationality\s*</[^>]+>\s*([^<]{2,60})<',
        r'Nationality\s*:?\s*(?:Image:\s*Nationality:\s*)?([A-Za-z &-]{2,50})',
    ]
    for pattern in patterns:
        match = re.search(pattern, text, flags=re.I | re.S)
        if match:
            value = clean_text(match.group(1))
            value = re.sub(r"\s+(?:Image|Birth Place|Billed From).*$", "", value, flags=re.I)
            if value:
                return value
    return ""


def existing_wikipedia_url(row: dict, sources: dict) -> str:
    for source_id in row.get("source_ids", "").split(";"):
        url = sources.get(source_id, {}).get("url", "")
        if "en.wikipedia.org/wiki/" in url:
            return url
    return ""


def wikipedia_identity(row: dict, sources: dict) -> tuple[str, str, str]:
    existing = existing_wikipedia_url(row, sources)
    if existing:
        title = urllib.parse.unquote(existing.split("/wiki/", 1)[1]).replace("_", " ")
    else:
        queries = []
        if row.get("real_name") and row.get("real_name_status") != "UNKNOWN":
            queries.append(row["real_name"])
        queries.extend([f'{row["ring_name"]} wrestler', row["ring_name"]])
        title = ""
        for query in queries:
            result = api("https://en.wikipedia.org/w/api.php", {
                "action": "query", "list": "search", "srsearch": query,
                "srnamespace": 0, "srlimit": 5, "format": "json", "utf8": 1,
            })
            for hit in result.get("query", {}).get("search", []):
                snippet = clean_text(hit.get("snippet", "")).lower()
                candidate = hit.get("title", "")
                identity_tokens = [norm(row["ring_name"]), norm(row.get("real_name", ""))]
                if ("wrestl" in snippet or "wrestl" in candidate.lower()) and any(
                    token and (token in norm(candidate) or norm(candidate) in token) for token in identity_tokens
                ):
                    title = candidate
                    break
            if title:
                break
    if not title:
        return "", "", ""

    page = api("https://en.wikipedia.org/w/api.php", {
        "action": "query", "prop": "pageprops|extracts", "titles": title,
        "exintro": 1, "explaintext": 1, "format": "json", "redirects": 1,
    })
    pages = list(page.get("query", {}).get("pages", {}).values())
    if not pages:
        return "", "", ""
    resolved_title = pages[0].get("title", title)
    qid = pages[0].get("pageprops", {}).get("wikibase_item", "")
    extract = pages[0].get("extract", "")
    wiki_url = "https://en.wikipedia.org/wiki/" + urllib.parse.quote(resolved_title.replace(" ", "_"))
    return wiki_url, qid, extract


def wikidata_nationality(qid: str) -> list[str]:
    if not qid:
        return []
    entity = api("https://www.wikidata.org/w/api.php", {
        "action": "wbgetentities", "ids": qid, "props": "claims", "format": "json",
    }).get("entities", {}).get(qid, {})
    country_ids = []
    for claim in entity.get("claims", {}).get("P27", []):
        value = claim.get("mainsnak", {}).get("datavalue", {}).get("value", {})
        if isinstance(value, dict) and value.get("id"):
            country_ids.append(value["id"])
    if not country_ids:
        return []
    labels = api("https://www.wikidata.org/w/api.php", {
        "action": "wbgetentities", "ids": "|".join(country_ids),
        "props": "labels", "languages": "en", "format": "json",
    }).get("entities", {})
    return [labels[q].get("labels", {}).get("en", {}).get("value", q) for q in country_ids]


def canonical(values: list[str]) -> str:
    mapped = []
    for value in values:
        item = COUNTRY_TO_DEMONYM.get(value.strip(), value.strip())
        if item and item not in mapped:
            mapped.append(item)
    return "-".join(mapped)


def research_one(row: dict, sources: dict, profiles: list[str]) -> dict:
    result = {
        "wrestler_id": row["wrestler_id"], "ring_name": row["ring_name"],
        "real_name": row.get("real_name", ""), "wikipedia_url": "",
        "wikipedia_nationality_raw": "", "sdh_url": "", "sdh_nationality_raw": "",
        "proposed_nationality": "", "proposed_status": "", "review_note": "",
    }
    try:
        wiki_url, qid, extract = wikipedia_identity(row, sources)
        wiki_values = wikidata_nationality(qid)
        result["wikipedia_url"] = wiki_url
        result["wikipedia_nationality_raw"] = ";".join(wiki_values)
        if wiki_url and not ("wrestl" in extract.lower() or row["ring_name"].lower() in extract.lower()):
            result["review_note"] = "Wikipedia identity requires review"
    except Exception as exc:
        result["review_note"] = f"Wikipedia lookup failed: {type(exc).__name__}"
        wiki_values = []
    try:
        sdh_url = sdh_candidate(row, profiles)
        result["sdh_url"] = sdh_url
        sdh_value = parse_sdh(sdh_url)
        result["sdh_nationality_raw"] = sdh_value
    except Exception as exc:
        sdh_value = ""
        result["review_note"] = (result["review_note"] + "; " if result["review_note"] else "") + f"SDH lookup failed: {type(exc).__name__}"

    wiki = canonical(wiki_values)
    sdh = canonical([sdh_value]) if sdh_value else ""
    if wiki and sdh and wiki == sdh:
        result["proposed_nationality"] = wiki
        result["proposed_status"] = "CONFIRMED"
    elif wiki and not sdh:
        result["proposed_nationality"] = wiki
        result["proposed_status"] = "PROBABLE"
    elif sdh and not wiki:
        result["proposed_nationality"] = sdh
        result["proposed_status"] = "PROBABLE"
    elif wiki and sdh:
        result["proposed_status"] = "CONFLICTING"
        result["review_note"] = (result["review_note"] + "; " if result["review_note"] else "") + f"Wikipedia={wiki}; SDH={sdh}"
    else:
        result["proposed_status"] = "UNKNOWN"
    return result


def main():
    with (DATA / "wrestlers.csv").open(newline="", encoding="utf-8-sig") as handle:
        wrestlers = [row for row in csv.DictReader(handle) if not row.get("nationality")]
    with (DATA / "sources.csv").open(newline="", encoding="utf-8-sig") as handle:
        sources = {row["source_id"]: row for row in csv.DictReader(handle)}

    profiles = load_sdh_profiles()
    print(f"Loaded {len(profiles)} wrestler profile URLs; researching {len(wrestlers)} blank nationalities.", flush=True)
    results = []
    with ThreadPoolExecutor(max_workers=8) as pool:
        futures = {pool.submit(research_one, row, sources, profiles): row for row in wrestlers}
        for index, future in enumerate(as_completed(futures), 1):
            results.append(future.result())
            if index % 25 == 0:
                print(f"Completed {index}/{len(wrestlers)}", flush=True)
            time.sleep(0.01)

    results.sort(key=lambda row: row["wrestler_id"])
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(results[0]))
        writer.writeheader()
        writer.writerows(results)
    counts = {}
    for row in results:
        counts[row["proposed_status"]] = counts.get(row["proposed_status"], 0) + 1
    print(f"Wrote {OUT}; status counts: {counts}")


if __name__ == "__main__":
    main()
