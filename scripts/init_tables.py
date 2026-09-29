"""Creates empty CSV files (headers only) for every table in the schema.
Safe to re-run: will NOT overwrite a file that already has data rows.
"""
import csv
import os
from schema import TABLES, DERIVED_TABLES

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
DERIVED_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "derived")
os.makedirs(DERIVED_DIR, exist_ok=True)


def init(path, fields):
    if os.path.exists(path):
        with open(path, "r", newline="", encoding="utf-8") as f:
            has_rows = len(f.readlines()) > 1
        if has_rows:
            print(f"skip (has data): {os.path.basename(path)}")
            return
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
    print(f"initialized: {os.path.basename(path)}")


for filename, fields in TABLES.items():
    init(os.path.join(DATA_DIR, filename), fields)

for filename, fields in DERIVED_TABLES.items():
    init(os.path.join(DERIVED_DIR, filename), fields)
