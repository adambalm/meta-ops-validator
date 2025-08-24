#!/usr/bin/env python3
"""
Fix datetime format issues in the database
Convert non-ISO date strings to proper date formats
"""
import sqlite3
from datetime import datetime, date
from dateutil import parser
import re

def fix_date_formats():
    """Fix all date format issues in the database"""
    
    db = sqlite3.connect('/tmp/metaops_demo.db')
    cursor = db.cursor()
    
    print("🔧 Fixing publication date formats...")
    
    # Get all books with problematic dates
    books = cursor.execute("""
        SELECT id, title, publication_date 
        FROM books 
        WHERE publication_date IS NOT NULL
    """).fetchall()
    
    fixed_count = 0
    
    for book_id, title, pub_date in books:
        if pub_date is not None:
            try:
                # Handle different data types
                if isinstance(pub_date, int):
                    # Year only - convert to YYYY-01-01
                    iso_date = f"{pub_date}-01-01"
                    cursor.execute("""
                        UPDATE books 
                        SET publication_date = ? 
                        WHERE id = ?
                    """, (iso_date, book_id))
                    print(f"   ✅ Fixed int: {title[:30]}... - {pub_date} → {iso_date}")
                    fixed_count += 1
                    
                elif isinstance(pub_date, str):
                    # Handle various string date formats
                    if re.match(r'^\d{4}-\d{2}-\d{2}$', pub_date):  # Already ISO format
                        continue
                        
                    # Parse common formats like "Aug 14, 2018", "2018", "2018-08", etc.
                    try:
                        parsed_date = parser.parse(pub_date, default=datetime(2024, 1, 1))
                        iso_date = parsed_date.strftime('%Y-%m-%d')
                        
                        # Update the database
                        cursor.execute("""
                            UPDATE books 
                            SET publication_date = ? 
                            WHERE id = ?
                        """, (iso_date, book_id))
                        
                        print(f"   ✅ Fixed str: {title[:30]}... - {pub_date} → {iso_date}")
                        fixed_count += 1
                        
                    except Exception as parse_error:
                        # If we can't parse it, set to a default
                        default_date = '2024-01-01'
                        cursor.execute("""
                            UPDATE books 
                            SET publication_date = ? 
                            WHERE id = ?
                        """, (default_date, book_id))
                        
                        print(f"   ⚠️  Defaulted str: {title[:30]}... - {pub_date} → {default_date}")
                        fixed_count += 1
                else:
                    # Handle any other data types
                    default_date = '2024-01-01'
                    cursor.execute("""
                        UPDATE books 
                        SET publication_date = ? 
                        WHERE id = ?
                    """, (default_date, book_id))
                    
                    print(f"   ⚠️  Defaulted other: {title[:30]}... - {type(pub_date)} → {default_date}")
                    fixed_count += 1
                        
            except Exception as e:
                print(f"   ❌ Error processing {title}: {e}")
    
    # Commit changes
    db.commit()
    db.close()
    
    print(f"\n🎉 Fixed {fixed_count} date format issues!")
    print("Database should now work properly with SQLAlchemy date processing.")
    
if __name__ == "__main__":
    fix_date_formats()