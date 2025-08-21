import csv
from pathlib import Path
from typing import List, Dict

# Presence scoring from a CSV (isbn,title,cover_url?,description?,categories?,age_range?)
# Avoid live scraping; data should be curated or API-cached.
def score_presence(csv_path: Path) -> List[Dict]:
    rows: List[Dict] = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            score = 0
            fields = ["cover_url", "description", "categories", "age_range"]
            for field in fields:
                val = (r.get(field) or "").strip()
                if val: score += 1
            rows.append({
                "isbn": r.get("isbn", ""),
                "title": r.get("title", ""),
                "cover_present": 1 if (r.get("cover_url") or "").strip() else 0,
                "description_present": 1 if (r.get("description") or "").strip() else 0,
                "categories_present": 1 if (r.get("categories") or "").strip() else 0,
                "age_range_present": 1 if (r.get("age_range") or "").strip() else 0,
                "presence_score": score  # 0..4
            })
    return rows