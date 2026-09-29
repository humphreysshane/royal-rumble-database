#!/usr/bin/env python3
"""Resolve combined-name TheSmackDownHotel profile URLs for unmatched aliases."""

from __future__ import annotations

import csv
import html
import re
import unicodedata
import urllib.request
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "research" / "nationality_sweep_20260928.csv"
UA = "Mozilla/5.0"
MAP = {
    "United States": "American", "Canada": "Canadian", "England": "English",
    "Scotland": "Scottish", "Wales": "Welsh", "United Kingdom": "British",
    "Ireland": "Irish", "Mexico": "Mexican", "Puerto Rico": "Puerto Rican",
    "Brazil": "Brazilian", "Argentina": "Argentine", "Italy": "Italian",
    "France": "French", "Germany": "German", "Switzerland": "Swiss",
    "Netherlands": "Dutch", "Spain": "Spanish", "Portugal": "Portuguese",
    "Greece": "Greek", "Poland": "Polish", "Russia": "Russian",
    "Australia": "Australian", "New Zealand": "New Zealander", "Fiji": "Fijian",
    "Samoa": "Samoan", "Tonga": "Tongan", "Japan": "Japanese", "China": "Chinese",
    "India": "Indian", "Iran": "Iranian", "Turkey": "Turkish",
    "South Africa": "South African", "Nigeria": "Nigerian", "Ghana": "Ghanaian",
}


def fetch(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as response:
        return response.read().decode("utf-8", "ignore")


def norm(value: str) -> str:
    value = unicodedata.normalize("NFKD", value or "").encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "", value.lower())


def profiles() -> list[str]:
    root = ET.fromstring(fetch("https://www.thesmackdownhotel.com/sitemap.xml"))
    urls = []
    for loc in root.findall("{*}sitemap/{*}loc"):
        tree = ET.fromstring(fetch(loc.text))
        urls += [n.text for n in tree.findall("{*}url/{*}loc") if n.text and "/wrestlers/" in n.text]
    return sorted(set(urls))


def candidate(row: dict, urls: list[str]) -> str:
    keys = [norm(row["wrestler_id"]), norm(row["ring_name"])]
    # Avoid generic one-word real names producing false matches.
    real = norm(row.get("real_name", ""))
    if len(real) >= 8:
        keys.append(real)
    keys = [key for key in keys if len(key) >= 4]
    matches = []
    for url in urls:
        slug = norm(url.rstrip("/").rsplit("/", 1)[-1])
        if any(key in slug for key in keys):
            matches.append(url)
    return matches[0] if len(matches) == 1 else ""


def parse(url: str) -> str:
    page = fetch(url)
    match = re.search(r'alt=["\']Nationality:\s*([^"\']+)', page, flags=re.I)
    if not match:
        return ""
    raw = re.sub(r"\s+", " ", html.unescape(match.group(1))).strip()
    return MAP.get(raw, raw)


def main():
    with MANIFEST.open(newline="", encoding="utf-8-sig") as handle:
        rows = list(csv.DictReader(handle))
    urls = profiles()
    targets = [row for row in rows if not row["sdh_url"]]
    selected = [(row, candidate(row, urls)) for row in targets]
    selected = [(row, url) for row, url in selected if url]
    print(f"Found unique combined-name profiles for {len(selected)} of {len(targets)} unmatched rows.", flush=True)
    with ThreadPoolExecutor(max_workers=6) as pool:
        futures = {pool.submit(parse, url): (row, url) for row, url in selected}
        for future in as_completed(futures):
            row, url = futures[future]
            try:
                value = future.result()
            except Exception:
                continue
            if value:
                row["sdh_url"] = url
                row["sdh_nationality_raw"] = value
                wiki = row["wikipedia_nationality_raw"]
                if wiki and wiki == value:
                    row["proposed_nationality"] = value
                    row["proposed_status"] = "CONFIRMED"
                    row["review_note"] = ""
                elif wiki and wiki != value:
                    row["proposed_status"] = "CONFLICTING"
                    row["review_note"] = f"Wikipedia={wiki}; SDH={value}"
                else:
                    row["proposed_nationality"] = value
                    row["proposed_status"] = "PROBABLE"
                    row["review_note"] = ""
    with MANIFEST.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader(); writer.writerows(rows)
    counts = {}
    for row in rows: counts[row["proposed_status"]] = counts.get(row["proposed_status"], 0) + 1
    print(f"Status counts: {counts}")


if __name__ == "__main__": main()
