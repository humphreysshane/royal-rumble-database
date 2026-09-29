#!/usr/bin/env python3
"""Capture every nationality badge from matched SDH profiles, not only the first."""

from __future__ import annotations

import csv
import html
import re
import urllib.request
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
    "India": "Indian", "Iran": "Iranian", "Turkey": "Turkish", "South Africa": "South African",
    "Nigeria": "Nigerian", "Ghana": "Ghanaian", "Guyana": "Guyanese",
    "Bulgaria": "Bulgarian", "Ukraine": "Ukrainian",
}
URL_FIXES = {
    "hakushi": "https://www.thesmackdownhotel.com/wrestlers/jinsei-shinzaki-hakushi",
}


def parse(url: str) -> tuple[str, str]:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as response:
        page = response.read().decode("utf-8", "ignore")
    raw = []
    for value in re.findall(r'alt=["\']Nationality:\s*([^"\']+)', page, flags=re.I):
        value = re.sub(r"\s+", " ", html.unescape(value)).strip()
        if value not in raw: raw.append(value)
    mapped = [MAP.get(value, value) for value in raw]
    return ";".join(raw), "-".join(mapped)


def main():
    with MANIFEST.open(newline="", encoding="utf-8-sig") as handle:
        rows = list(csv.DictReader(handle))
    for row in rows:
        if row["wrestler_id"] in URL_FIXES:
            row["sdh_url"] = URL_FIXES[row["wrestler_id"]]
    targets = [row for row in rows if row["sdh_url"]]
    with ThreadPoolExecutor(max_workers=6) as pool:
        futures = {pool.submit(parse, row["sdh_url"]): row for row in targets}
        for index, future in enumerate(as_completed(futures), 1):
            row = futures[future]
            try:
                raw, value = future.result()
            except Exception:
                continue
            if not value: continue
            row["sdh_nationality_raw"] = raw
            row["proposed_nationality"] = value
            wiki = row["wikipedia_nationality_raw"]
            if wiki and wiki == value:
                row["proposed_status"] = "CONFIRMED"; row["review_note"] = ""
            elif wiki and wiki != value:
                # Preserve both observations for review; application overrides handle
                # manually reviewed citizenship-vs-birth-country cases.
                row["proposed_status"] = "CONFLICTING"
                row["review_note"] = f"Wikipedia={wiki}; SDH={value}"
            else:
                row["proposed_status"] = "PROBABLE"; row["review_note"] = ""
            if index % 50 == 0: print(f"Audited {index}/{len(targets)}", flush=True)
    with MANIFEST.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0])); writer.writeheader(); writer.writerows(rows)
    dual = [row for row in rows if ";" in row["sdh_nationality_raw"]]
    print(f"Captured {len(dual)} dual/multiple-nationality profiles.")
    for row in dual:
        print(row["wrestler_id"], row["sdh_nationality_raw"], "=>", row["proposed_nationality"])


if __name__ == "__main__": main()
