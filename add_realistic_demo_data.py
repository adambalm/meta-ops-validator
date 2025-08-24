#!/usr/bin/env python3
"""
Add realistic demo data showing ONIX validation scenarios
"""
import sqlite3
import uuid
from datetime import datetime, timedelta
import json

def add_realistic_data():
    db = sqlite3.connect('/tmp/metaops_demo.db')
    cursor = db.cursor()
    
    # Update some existing books with different validation statuses
    realistic_books = [
        {
            'isbn': '9780123456791', 
            'validation_status': 'approved',
            'onix_compliance': 'pass',
            'notes': 'Full ONIX compliance - ready for distribution'
        },
        {
            'isbn': '9780123456794',
            'validation_status': 'rejected', 
            'onix_compliance': 'fail',
            'notes': 'Missing required contributors, price format invalid'
        },
        {
            'isbn': '9780123456790',
            'validation_status': 'under_review',
            'onix_compliance': 'warning', 
            'notes': 'Minor issues: missing marketing copy, subject codes incomplete'
        }
    ]
    
    for book in realistic_books:
        cursor.execute("""
            UPDATE books 
            SET validation_status = ?, updated_at = ?
            WHERE isbn = ?
        """, (book['validation_status'], datetime.now(), book['isbn']))
        print(f"Updated {book['isbn']} -> {book['validation_status']}")
    
    # Add more realistic contracts
    publishers = cursor.execute("SELECT DISTINCT id FROM publishers").fetchall()
    if not publishers:
        print("No publishers found!")
        return
        
    publisher_id = publishers[0][0]
    
    new_contracts = [
        {
            'id': str(uuid.uuid4()),
            'publisher_id': publisher_id,
            'contract_name': 'Ingram Content Group Agreement', 
            'contract_type': 'distribution_agreement',
            'retailer': 'ingram_content',
            'effective_date': '2025-01-01',
            'expiration_date': '2026-12-31',
            'territory_restrictions': '["US", "CA", "UK", "AU", "NZ"]',
            'validation_rules': json.dumps({
                "required_fields": ["isbn", "title", "contributor", "price", "publication_date", "description"],
                "min_discount": 0.35,
                "max_price": 100.0,
                "require_bisac_codes": True,
                "min_description_length": 50
            }),
            'status': 'active'
        },
        {
            'id': str(uuid.uuid4()), 
            'publisher_id': publisher_id,
            'contract_name': 'Kobo Inc Distribution Terms',
            'contract_type': 'distribution_agreement', 
            'retailer': 'kobo',
            'effective_date': '2025-03-15',
            'territory_restrictions': '["CA", "US", "UK", "FR", "DE", "IT"]',
            'validation_rules': json.dumps({
                "required_fields": ["isbn", "title", "contributor", "price"],
                "min_discount": 0.25,
                "max_price": 75.0,
                "require_drm": True,
                "supported_formats": ["epub", "pdf"]
            }),
            'status': 'pending'
        },
        {
            'id': str(uuid.uuid4()),
            'publisher_id': publisher_id, 
            'contract_name': 'Google Play Books Partnership',
            'contract_type': 'revenue_share',
            'retailer': 'google_play',
            'effective_date': '2025-02-01',
            'territory_restrictions': '["WORLD"]',
            'validation_rules': json.dumps({
                "required_fields": ["isbn", "title", "contributor", "price", "publication_date"],
                "revenue_share": 0.7,
                "require_preview": True,
                "max_file_size_mb": 100
            }),
            'status': 'under_review'
        }
    ]
    
    for contract in new_contracts:
        cursor.execute("""
            INSERT INTO contracts 
            (id, publisher_id, contract_name, contract_type, retailer, effective_date, 
             expiration_date, territory_restrictions, validation_rules, status, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            contract['id'], contract['publisher_id'], contract['contract_name'],
            contract['contract_type'], contract['retailer'], contract['effective_date'],
            contract.get('expiration_date'), contract['territory_restrictions'],
            contract['validation_rules'], contract['status'],
            datetime.now(), datetime.now()
        ))
        print(f"Added contract: {contract['contract_name']}")
    
    # Add some validation history/compliance checks
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS validation_history (
            id VARCHAR(36) PRIMARY KEY,
            book_id VARCHAR(36),
            validation_type VARCHAR(50),
            status VARCHAR(20), 
            issues TEXT,
            checked_at DATETIME,
            FOREIGN KEY (book_id) REFERENCES books(id)
        )
    """)
    
    # Get some book IDs
    book_ids = cursor.execute("SELECT id FROM books LIMIT 3").fetchall()
    
    validation_scenarios = [
        {
            'book_id': book_ids[0][0],
            'validation_type': 'onix_xsd',
            'status': 'pass',
            'issues': '[]'
        },
        {
            'book_id': book_ids[0][0], 
            'validation_type': 'onix_schematron',
            'status': 'pass',
            'issues': '[]'
        },
        {
            'book_id': book_ids[1][0],
            'validation_type': 'onix_xsd', 
            'status': 'fail',
            'issues': json.dumps([
                {"level": "ERROR", "message": "Required element 'ProductIdentifier' is missing"},
                {"level": "ERROR", "message": "Invalid ISBN format in element 'IDValue'"}
            ])
        },
        {
            'book_id': book_ids[2][0],
            'validation_type': 'nielsen_scoring',
            'status': 'warning',
            'issues': json.dumps([
                {"level": "WARNING", "message": "Marketing copy is missing - impacts discoverability"},
                {"level": "WARNING", "message": "Only 1 BISAC subject code provided, recommended 3+"}
            ])
        }
    ]
    
    for val in validation_scenarios:
        val_id = str(uuid.uuid4())
        cursor.execute("""
            INSERT INTO validation_history 
            (id, book_id, validation_type, status, issues, checked_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (val_id, val['book_id'], val['validation_type'], val['status'], 
              val['issues'], datetime.now() - timedelta(hours=2)))
    
    print("Added validation history")
    
    db.commit()
    db.close()
    print("✅ Realistic demo data added successfully!")

if __name__ == "__main__":
    add_realistic_data()