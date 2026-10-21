import csv
import os
import sys
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent
output_file = str(PROJECT_DIR / "output" / "gmail_test.csv")

new_csv = sys.stdin.read().strip()

if not new_csv:
    raise ValueError("No new CSV data provided.")

rows = list(csv.DictReader(new_csv.splitlines()))
if not rows:
    raise ValueError("No email rows found in CSV data.")

fieldnames = list(rows[0].keys())
os.makedirs(os.path.dirname(output_file), exist_ok=True)

file_exists = os.path.exists(output_file) and os.path.getsize(output_file) > 0

with open(output_file, 'a', newline='', encoding='utf-8-sig') as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)

    if not file_exists:
        writer.writeheader()

    writer.writerows(rows)

print(f"Appended {len(rows)} email(s) to {output_file}")

