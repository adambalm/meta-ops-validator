#!/usr/bin/env python3
"""Debug database date issues"""
import sqlite3

db = sqlite3.connect('/tmp/metaops_demo.db')
cursor = db.cursor()

print("🔍 Analyzing publication_date column...")

# Check all publication dates
cursor.execute("SELECT id, title, publication_date, typeof(publication_date) FROM books LIMIT 20")
rows = cursor.fetchall()

for book_id, title, pub_date, data_type in rows:
    print(f"{title[:30]:<30} | {pub_date} | Type: {data_type}")

print(f"\n📊 Data type distribution:")
cursor.execute("SELECT typeof(publication_date), COUNT(*) FROM books GROUP BY typeof(publication_date)")
type_counts = cursor.fetchall()

for data_type, count in type_counts:
    print(f"  {data_type}: {count} records")

print(f"\n❓ Checking for NULL values:")
cursor.execute("SELECT COUNT(*) FROM books WHERE publication_date IS NULL")
null_count = cursor.fetchone()[0]
print(f"  NULL values: {null_count}")

print(f"\n❓ Checking for empty strings:")
cursor.execute("SELECT COUNT(*) FROM books WHERE publication_date = ''")
empty_count = cursor.fetchone()[0]  
print(f"  Empty strings: {empty_count}")

db.close()