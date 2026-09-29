#!/usr/bin/env python3
"""Retry Wikipedia evidence at a conservative request rate and enrich manifest."""

from __future__ import annotations

import csv
import html
import json
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
MANIFEST = ROOT / "research" / "nationality_sweep_20260928.csv"
UA = "Mozilla/5.0 (compatible; RoyalRumbleDatabaseResearch/1.0)"

DEMONYMS = [
    "Northern Irish", "New Zealander", "South African", "South Korean", "Saudi Arabian",
    "Puerto Rican", "Fijian-American", "Mexican-American", "Canadian-American",
    "British-American", "Japanese-American", "Samoan-American", "Tongan-American",
    "American", "Canadian", "English", "Scottish", "Welsh", "British", "Irish",
    "Mexican", "Puerto Rican", "Cuban", "Dominican", "Haitian", "Jamaican",
    "Trinidadian", "Brazilian", "Argentine", "Chilean", "Colombian", "Guyanese",
    "Italian", "French", "German", "Austrian", "Swiss", "Dutch", "Belgian",
    "Spanish", "Portuguese", "Greek", "Polish", "Russian", "Ukrainian", "Bulgarian",
    "Romanian", "Croatian", "Serbian", "Finnish", "Swedish", "Norwegian", "Danish",
    "Icelandic", "Australian", "Fijian", "Samoan", "Tongan", "Japanese", "Chinese",
    "Taiwanese", "Indian", "Pakistani", "Iranian", "Iraqi", "Israeli", "Turkish",
    "Nigerian", "Ghanaian", "Ugandan", "Cameroonian", "Egyptian",
]


def fetch_json(params: dict) -> dict:
    url = "https://en.wikipedia.org/w/api.php?" + urllib.parse.urlencode(params)
    for attempt in range(7):
        try:
            request = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "en"})
            with urllib.request.urlopen(request, timeout=30) as response:
                return json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            if exc.code not in (429, 500, 502, 503, 504) or attempt == 6:
                raise
            time.sleep(2 ** attempt)
        except (TimeoutError, urllib.error.URLError):
            if attempt == 6:
                raise
            time.sleep(2 ** attempt)
    return {}


def norm(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", (value or "").lower())


def strip_tags(value: str) -> str:
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", value))).strip()


def find_title(row: dict, sources: dict) -> str:
    for source_id in sources.get(row["wrestler_id"], "").split(";"):
        url = source_urls.get(source_id, "")
        if "en.wikipedia.org/wiki/" in url:
            return urllib.parse.unquote(url.split("/wiki/", 1)[1]).replace("_", " ")
    queries = []
    if row.get("real_name"):
        queries.append(row["real_name"])
    queries += [f'{row["ring_name"]} professional wrestler', row["ring_name"]]
    identity = {norm(row["ring_name"]), norm(row.get("real_name", ""))} - {""}
    fallback = ""
    for query in queries:
        result = fetch_json({
            "action": "query", "list": "search", "srsearch": query,
            "srnamespace": 0, "srlimit": 5, "format": "json", "utf8": 1,
        })
        for hit in result.get("query", {}).get("search", []):
            title = hit.get("title", "")
            snippet = strip_tags(hit.get("snippet", ""))
            if not fallback and "wrestl" in (title + " " + snippet).lower():
                fallback = title
            if "wrestl" in (title + " " + snippet).lower() and any(
                token in norm(title) or norm(title) in token or token in norm(snippet)
                for token in identity
            ):
                return title
    return fallback


def extract_intro(title: str) -> tuple[str, str]:
    if not title:
        return "", ""
    result = fetch_json({
        "action": "query", "prop": "extracts", "titles": title,
        "exintro": 1, "explaintext": 1, "redirects": 1, "format": "json",
    })
    pages = list(result.get("query", {}).get("pages", {}).values())
    if not pages:
        return "", ""
    resolved = pages[0].get("title", title)
    return resolved, pages[0].get("extract", "")


def nationality_from_intro(intro: str) -> str:
    opening = intro[:800]
    hits = []
    for value in DEMONYMS:
        if re.search(rf"\b{re.escape(value)}\b", opening, flags=re.I):
            if value not in hits:
                hits.append(value)
    # The first nationality adjective in a biography opening is normally the
    # article's explicit descriptor. Preserve a hyphenated dual descriptor.
    return hits[0] if hits else ""


def lookup(row: dict, wrestler_sources: dict) -> tuple[str, str, str]:
    title = find_title(row, wrestler_sources)
    resolved, intro = extract_intro(title)
    url = "https://en.wikipedia.org/wiki/" + urllib.parse.quote(resolved.replace(" ", "_")) if resolved else ""
    nationality = nationality_from_intro(intro)
    note = ""
    if resolved and not nationality:
        note = "Wikipedia article found but opening nationality descriptor not parsed"
    return url, nationality, note


def main():
    global source_urls
    with (DATA / "sources.csv").open(newline="", encoding="utf-8-sig") as handle:
        source_urls = {row["source_id"]: row.get("url", "") for row in csv.DictReader(handle)}
    with (DATA / "wrestlers.csv").open(newline="", encoding="utf-8-sig") as handle:
        wrestler_sources = {row["wrestler_id"]: row.get("source_ids", "") for row in csv.DictReader(handle)}
    with MANIFEST.open(newline="", encoding="utf-8-sig") as handle:
        rows = list(csv.DictReader(handle))

    with ThreadPoolExecutor(max_workers=2) as pool:
        futures = {pool.submit(lookup, row, wrestler_sources): row for row in rows}
        for index, future in enumerate(as_completed(futures), 1):
            row = futures[future]
            try:
                url, nationality, note = future.result()
                row["wikipedia_url"] = url
                row["wikipedia_nationality_raw"] = nationality
                if note:
                    row["review_note"] = note
            except Exception as exc:
                row["review_note"] = f"Wikipedia retry failed: {type(exc).__name__}"
            if index % 25 == 0:
                print(f"Wikipedia completed {index}/{len(rows)}", flush=True)

    for row in rows:
        wiki = row["wikipedia_nationality_raw"]
        sdh = row["proposed_nationality"] if row["sdh_nationality_raw"] else ""
        if wiki and sdh and wiki == sdh:
            row["proposed_nationality"] = wiki
            row["proposed_status"] = "CONFIRMED"
            row["review_note"] = ""
        elif wiki and not sdh:
            row["proposed_nationality"] = wiki
            row["proposed_status"] = "PROBABLE"
        elif wiki and sdh and wiki != sdh:
            row["proposed_status"] = "CONFLICTING"
            row["review_note"] = f"Wikipedia={wiki}; SDH={sdh}"

    with MANIFEST.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    counts = {}
    for row in rows:
        counts[row["proposed_status"]] = counts.get(row["proposed_status"], 0) + 1
    print(f"Updated {MANIFEST}; status counts: {counts}")


if __name__ == "__main__":
    main()
