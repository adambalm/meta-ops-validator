#!/usr/bin/env python3
"""
Fetch real book data from public APIs to make demo more authentic
"""
import requests
import sqlite3
import uuid
from datetime import datetime
import json
import time

def fetch_openlibrary_data(isbn):
    """Fetch book data from OpenLibrary API"""
    try:
        url = f"https://openlibrary.org/isbn/{isbn}.json"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        print(f"Error fetching {isbn}: {e}")
    return None

def fetch_google_books_data(isbn):
    """Fetch book data from Google Books API"""
    try:
        url = f"https://www.googleapis.com/books/v1/volumes?q=isbn:{isbn}"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get('items'):
                return data['items'][0]['volumeInfo']
    except Exception as e:
        print(f"Error fetching Google Books {isbn}: {e}")
    return None

def add_real_book_data():
    """Add real book data to demo database"""
    
    # Popular books with known ISBNs for authentic data
    real_books = [
        # Classic Literature (OpenLibrary strong)
        "9780061120084",  # To Kill a Mockingbird
        "9780141439518",  # Pride and Prejudice
        "9780142437261",  # Of Mice and Men
        "9780486284712",  # Great Gatsby
        
        # Contemporary Fiction (Google Books strong)
        "9780143039952",  # The Kite Runner  
        "9780307277671",  # The Girl with the Dragon Tattoo
        "9780439708180",  # Harry Potter and the Sorcerer's Stone
        "9780061122415",  # The Alchemist
        
        # Technical/Business Books (Google Books better metadata)
        "9780134685991",  # Effective Java
        "9781492040343",  # Designing Data-Intensive Applications  
        "9780321125217",  # Domain-Driven Design
        "9780596517748",  # JavaScript: The Good Parts
        
        # Recent Bestsellers (Mixed sources)
        "9780385547345",  # Educated: A Memoir
        "9780735219090",  # Where the Crawdads Sing
    ]
    
    db = sqlite3.connect('/tmp/metaops_demo.db')
    cursor = db.cursor()
    
    # Add metadata_source column if it doesn't exist
    try:
        cursor.execute("ALTER TABLE books ADD COLUMN metadata_source VARCHAR(50)")
        print("Added metadata_source column to books table")
        db.commit()
    except:
        pass  # Column already exists
    
    # Get a publisher ID
    publishers = cursor.execute("SELECT id FROM publishers LIMIT 1").fetchall()
    if not publishers:
        print("No publishers found!")
        return
        
    publisher_id = publishers[0][0]
    
    books_added = 0
    
    for isbn in real_books:
        print(f"Fetching data for ISBN: {isbn}")
        
        # Try OpenLibrary first
        book_data = fetch_openlibrary_data(isbn)
        data_source = None
        if book_data:
            data_source = "openlibrary"
        else:
            # Fallback to Google Books
            book_data = fetch_google_books_data(isbn)
            if book_data:
                data_source = "google_books"
            
        if book_data:
            # Extract data from OpenLibrary format
            if 'title' in book_data:
                title = book_data.get('title', 'Unknown Title')
                
                # Handle authors - different formats from different APIs
                authors = []
                if 'authors' in book_data:
                    if isinstance(book_data['authors'], list):
                        for author in book_data['authors']:
                            if isinstance(author, dict):
                                authors.append(author.get('name', ''))
                            elif isinstance(author, str):
                                authors.append(author)
                    
                # Get publication date
                pub_date = None
                if 'publish_date' in book_data:
                    pub_date = book_data['publish_date']
                elif 'publishedDate' in book_data:
                    pub_date = book_data['publishedDate']
                
                # Get description  
                description = book_data.get('description', '')
                if isinstance(description, dict):
                    description = description.get('value', '')
                elif isinstance(description, list):
                    description = ' '.join(description) if description else ''
                
                # Create realistic validation status
                validation_statuses = ['approved', 'pending', 'rejected', 'under_review']
                import random
                status = random.choice(validation_statuses)
                
                # Insert book
                book_id = str(uuid.uuid4())
                # Check if book already exists
                existing = cursor.execute("SELECT id FROM books WHERE isbn = ?", (isbn,)).fetchone()
                if existing:
                    print(f"📚 Skipping existing book: {title} ({isbn})")
                    continue
                    
                cursor.execute("""
                    INSERT INTO books 
                    (id, publisher_id, title, subtitle, isbn, publication_date, product_form, validation_status, metadata_source, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    book_id, publisher_id, title, 
                    description[:100] + "..." if len(description or "") > 100 else description or "",
                    isbn, pub_date or '2024-01-01', 'BC', status, data_source, datetime.now(), datetime.now()
                ))
                
                # Add some authors if we found them
                if authors:
                    for i, author_name in enumerate(authors[:2]):  # Max 2 authors
                        if author_name.strip():
                            author_id = str(uuid.uuid4())
                            cursor.execute("""
                                INSERT OR IGNORE INTO authors 
                                (id, name, biography, created_at, updated_at)
                                VALUES (?, ?, ?, ?, ?)
                            """, (
                                author_id, author_name.strip(), 
                                f"Biography for {author_name}",
                                datetime.now(), datetime.now()
                            ))
                            
                            # Link author to book
                            cursor.execute("""
                                INSERT OR IGNORE INTO book_authors
                                (book_id, author_id, sequence_number, contributor_role)
                                VALUES (?, ?, ?, ?)
                            """, (book_id, author_id, i + 1, 'A01'))
                
                print(f"✅ Added: {title} ({isbn}) - Status: {status} - Source: {data_source}")
                books_added += 1
                
        else:
            print(f"❌ Could not fetch data for {isbn}")
            
        # Be nice to APIs
        time.sleep(1)
    
    # Generate source analysis
    cursor.execute("SELECT metadata_source, COUNT(*), GROUP_CONCAT(title) FROM books WHERE metadata_source IS NOT NULL GROUP BY metadata_source")
    source_stats = cursor.fetchall()
    
    db.commit()
    db.close()
    
    print(f"\n🎉 Successfully added {books_added} real books to demo database!")
    print("These books now have authentic metadata from real publishing data.")
    
    print(f"\n📊 Data Source Analysis:")
    for source, count, titles in source_stats:
        print(f"  {source}: {count} books")
        sample_titles = titles.split(',')[:3]  # Show first 3 titles
        print(f"    Sample: {', '.join(sample_titles)}")
    
    print(f"\nTotal books in database: {sum(stat[1] for stat in source_stats)}")

if __name__ == "__main__":
    add_real_book_data()