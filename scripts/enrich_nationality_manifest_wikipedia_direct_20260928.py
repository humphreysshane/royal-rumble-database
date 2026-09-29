#!/usr/bin/env python3
"""Enrich the nationality manifest from directly rendered Wikipedia pages."""

from __future__ import annotations

import csv
import html
import re
import time
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
MANIFEST = ROOT / "research" / "nationality_sweep_20260928.csv"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/140 Safari/537.36"
DEMONYMS = [
    "Northern Irish", "New Zealander", "South African", "South Korean", "Saudi Arabian",
    "Puerto Rican", "Fijian-American", "Mexican-American", "Canadian-American",
    "British-American", "Japanese-American", "Samoan-American", "Tongan-American",
    "American", "Canadian", "English", "Scottish", "Welsh", "British", "Irish",
    "Mexican", "Cuban", "Dominican", "Haitian", "Jamaican", "Trinidadian", "Brazilian",
    "Argentine", "Chilean", "Colombian", "Guyanese", "Italian", "French", "German",
    "Austrian", "Swiss", "Dutch", "Belgian", "Spanish", "Portuguese", "Greek", "Polish",
    "Russian", "Ukrainian", "Bulgarian", "Romanian", "Croatian", "Serbian", "Finnish",
    "Swedish", "Norwegian", "Danish", "Icelandic", "Australian", "Fijian", "Samoan",
    "Tongan", "Japanese", "Chinese", "Taiwanese", "Indian", "Pakistani", "Iranian",
    "Iraqi", "Israeli", "Turkish", "Nigerian", "Ghanaian", "Ugandan", "Cameroonian",
    "Egyptian",
]


def fetch(url: str) -> tuple[str, str]:
    request = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "en"})
    with urllib.request.urlopen(request, timeout=25) as response:
        return response.geturl(), response.read().decode("utf-8", "ignore")


def visible(value: str) -> str:
    value = re.sub(r"<sup\b[^>]*>.*?</sup>", " ", value, flags=re.I | re.S)
    value = re.sub(r"<[^>]+>", " ", value)
    return re.sub(r"\s+", " ", html.unescape(value)).strip()


def direct_existing(row: dict, wrestler_source_ids: dict, source_urls: dict) -> str:
    for source_id in wrestler_source_ids.get(row["wrestler_id"], "").split(";"):
        url = source_urls.get(source_id, "")
        if "en.wikipedia.org/wiki/" in url:
            return url
    return ""


def parse_intro(page: str) -> str:
    article = re.search(r'<div[^>]+class="[^"]*(?:mw-content-ltr|mw-parser-output)[^"]*"[^>]*>(.*)', page, flags=re.I | re.S)
    body = article.group(1) if article else page
    for para in re.findall(r"<p\b[^>]*>(.*?)</p>", body, flags=re.I | re.S):
        text = visible(para)
        if len(text) > 80 and ("wrestl" in text.lower() or "announcer" in text.lower() or "commentator" in text.lower()):
            return text
    meta = re.search(r'<meta[^>]+name="description"[^>]+content="([^"]+)"', page, flags=re.I)
    return html.unescape(meta.group(1)) if meta else ""


def detect(intro: str) -> str:
    for value in DEMONYMS:
        if re.search(rf"\b{re.escape(value)}\b", intro[:1000], flags=re.I):
            return value
    return ""


def lookup(row: dict, wrestler_source_ids: dict, source_urls: dict) -> tuple[str, str, str]:
    url = direct_existing(row, wrestler_source_ids, source_urls)
    if not url:
        query = row.get("real_name") or row["ring_name"]
        url = "https://en.wikipedia.org/wiki/Special:Search?" + urllib.parse.urlencode({"search": query + " professional wrestler", "go": "Go"})
    resolved, page = fetch(url)
    intro = parse_intro(page)
    nationality = detect(intro)
    note = "" if nationality else "Wikipedia page/search did not yield an explicit nationality descriptor"
    return resolved.split("#", 1)[0], nationality, note


def main():
    with (DATA / "sources.csv").open(newline="", encoding="utf-8-sig") as handle:
        source_urls = {row["source_id"]: row.get("url", "") for row in csv.DictReader(handle)}
    with (DATA / "wrestlers.csv").open(newline="", encoding="utf-8-sig") as handle:
        wrestler_source_ids = {row["wrestler_id"]: row.get("source_ids", "") for row in csv.DictReader(handle)}
    with MANIFEST.open(newline="", encoding="utf-8-sig") as handle:
        rows = list(csv.DictReader(handle))

    with ThreadPoolExecutor(max_workers=6) as pool:
        futures = {pool.submit(lookup, row, wrestler_source_ids, source_urls): row for row in rows}
        for index, future in enumerate(as_completed(futures), 1):
            row = futures[future]
            try:
                url, nationality, note = future.result()
                row["wikipedia_url"] = url
                row["wikipedia_nationality_raw"] = nationality
                if note and not row["review_note"].startswith("Wikipedia="):
                    row["review_note"] = note
            except Exception as exc:
                row["review_note"] = f"Wikipedia direct lookup failed: {type(exc).__name__}"
            if index % 50 == 0:
                print(f"Wikipedia direct completed {index}/{len(rows)}", flush=True)
            time.sleep(0.005)

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
    print(f"Updated manifest; status counts: {counts}")


if __name__ == "__main__":
    main()
