"""Collect a dated Wikipedia alias snapshot for the unresolved title-link queue.

The output is a research aid. Nothing is written to the database and no
identity is accepted automatically.
"""

from __future__ import annotations

import csv
import json
import re
import time
import urllib.parse
import urllib.request
import urllib.error
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
AUDIT = ROOT / "research" / "championship_identity_audit_20260929"
OUT = ROOT / "research" / "wrestler_alias_snapshot_20260929.json"
API = "https://en.wikipedia.org/w/api.php"
UA = "RoyalRumbleDatabaseResearch/1.0 (championship identity audit)"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def api(params: dict[str, str]) -> dict:
    params = {"format": "json", "formatversion": "2", **params}
    url = API + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    for attempt in range(6):
        try:
            with urllib.request.urlopen(req, timeout=45) as response:
                return json.load(response)
        except urllib.error.HTTPError as exc:
            if exc.code != 429 or attempt == 5:
                raise
            time.sleep(3 * (attempt + 1))
    raise RuntimeError("unreachable")


def existing_page_title(row: dict[str, str], source_by_id: dict[str, dict[str, str]]) -> str:
    for source_id in row.get("source_ids", "").split(";"):
        url = source_by_id.get(source_id, {}).get("url", "")
        if "en.wikipedia.org/wiki/" in url:
            return urllib.parse.unquote(url.split("/wiki/", 1)[1]).replace("_", " ")
    return ""


def search_page(ring_name: str) -> tuple[str, list[str]]:
    result = api({
        "action": "query", "list": "search", "srlimit": "5",
        "srsearch": f'"{ring_name}" professional wrestler',
    })
    titles = [r["title"] for r in result.get("query", {}).get("search", [])]
    return (titles[0] if titles else ""), titles


def page_wikitext(title: str) -> tuple[str, str, str]:
    result = api({
        "action": "query", "prop": "revisions|info", "inprop": "url",
        "rvprop": "content", "rvslots": "main", "titles": title,
    })
    pages = result.get("query", {}).get("pages", [])
    if not pages or pages[0].get("missing"):
        return "", "", ""
    page = pages[0]
    text = page.get("revisions", [{}])[0].get("slots", {}).get("main", {}).get("content", "")
    return page.get("title", title), page.get("fullurl", ""), text


def clean_markup(value: str) -> str:
    value = re.sub(r"<!--.*?-->", "", value, flags=re.S)
    value = re.sub(r"<br\s*/?>", ";", value, flags=re.I)
    value = re.sub(r"\{\{(?:small|nowrap|ubl|unbulleted list|plainlist)\|", "", value, flags=re.I)
    value = value.replace("{{ubl", "").replace("{{unbulleted list", "")
    value = re.sub(r"\[\[(?:[^]|]+\|)?([^]]+)]]", r"\1", value)
    value = re.sub(r"<ref\b[^>]*>.*?</ref>|<ref\b[^>]*/>", "", value, flags=re.S | re.I)
    value = re.sub(r"\{\{[^{}]*}}", "", value)
    value = value.replace("}}", "").replace("''", "")
    value = re.sub(r"^[*#]+\s*", "", value.strip())
    return re.sub(r"\s+", " ", value).strip(" ;|")


def infobox_values(text: str, keys: tuple[str, ...]) -> list[str]:
    values = []
    for key in keys:
        match = re.search(
            rf"(?mi)^\|\s*{re.escape(key)}\s*=\s*(.*?)(?=\n\s*\|\s*[a-zA-Z_ ]+\s*=|\n}}}})",
            text,
            flags=re.S,
        )
        if match:
            value = clean_markup(match.group(1))
            values.extend(x.strip() for x in re.split(r";|\n", value) if x.strip())
    return list(dict.fromkeys(values))


def research(row: dict[str, str], source_by_id: dict[str, dict[str, str]]) -> dict[str, object]:
    known_title = existing_page_title(row, source_by_id)
    search_titles: list[str] = []
    title = known_title
    if not title:
        title, search_titles = search_page(row["ring_name"])
    if not title:
        return {"wrestler_id": row["wrestler_id"], "ring_name": row["ring_name"], "error": "no_search_result"}
    resolved_title, url, text = page_wikitext(title)
    return {
        "wrestler_id": row["wrestler_id"],
        "ring_name": row["ring_name"],
        "existing_aliases": [x.strip() for x in re.split(r"[;|]", row.get("aliases_ring_names", "")) if x.strip()],
        "page_title": resolved_title,
        "url": url,
        "page_selected_from_existing_source": bool(known_title),
        "search_candidates": search_titles,
        "birth_name": infobox_values(text, ("birth_name",)),
        "ring_names": infobox_values(text, ("names", "ring_names", "billed_name")),
        "wikitext_sha_length": len(text),
    }


def main() -> None:
    wrestlers = {r["wrestler_id"]: r for r in read_csv(DATA / "wrestlers.csv")}
    sources = {r["source_id"]: r for r in read_csv(DATA / "sources.csv")}
    queue_ids = [r["wrestler_id"] for r in read_csv(AUDIT / "rumble_wrestlers_without_linked_reigns.csv")]
    rows = [wrestlers[wrestler_id] for wrestler_id in queue_ids]
    previous = {}
    if OUT.exists():
        previous = {
            r["wrestler_id"]: r
            for r in json.loads(OUT.read_text(encoding="utf-8")).get("results", [])
            if not r.get("error")
        }
    results = []
    for row in rows:
        wrestler_id = row["wrestler_id"]
        if wrestler_id in previous:
            results.append(previous[wrestler_id])
            continue
        try:
            results.append(research(row, sources))
        except Exception as exc:
            results.append({"wrestler_id": wrestler_id, "error": f"{type(exc).__name__}: {exc}"})
        time.sleep(0.65)
    results.sort(key=lambda row: row["wrestler_id"])
    OUT.write_text(json.dumps({"accessed_date": "2026-09-29", "results": results}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    errors = sum(bool(r.get("error")) for r in results)
    print(f"Collected {len(results)} wrestler pages; {errors} errors; wrote {OUT}")


if __name__ == "__main__":
    main()
