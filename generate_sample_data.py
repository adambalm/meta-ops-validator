#!/usr/bin/env python3
"""
Generate sample data for MetaOps book-author-contract demo
"""
import requests
import json
from datetime import date, timedelta
from typing import List, Dict

# API Configuration
BASE_URL = "http://100.111.114.84:8002/api/v1"
AUTH_TOKEN = "demo.eyJ1c2VyX2lkIjoiZGVtb191c2VyIn0.signature"
HEADERS = {
    "Authorization": f"Bearer {AUTH_TOKEN}",
    "Content-Type": "application/json"
}

# Sample data configurations
PUBLISHERS = [
    {
        "name": "Atlantic Literary Press",
        "imprint": "Atlantic Books",
        "territory_codes": ["US", "CA"],
        "validation_profile": {"strict_mode": True, "auto_approve": False}
    },
    {
        "name": "Pacific Publishing House",
        "imprint": "Pacific Fiction",
        "territory_codes": ["US", "UK", "AU"],
        "validation_profile": {"strict_mode": False, "auto_approve": True}
    },
    {
        "name": "Mountain View Media",
        "imprint": "Mountain Reads",
        "territory_codes": ["US"],
        "validation_profile": {"strict_mode": True, "auto_approve": False}
    }
]

AUTHORS = [
    {
        "name": "Sarah Mitchell",
        "contributor_type": "A01",
        "biography": "Sarah Mitchell is a bestselling author of contemporary fiction, known for her compelling character-driven narratives.",
        "website_url": "https://sarahmitchell.com"
    },
    {
        "name": "David Chen",
        "contributor_type": "A01", 
        "biography": "David Chen is a science fiction writer whose work explores themes of technology and human connection.",
        "website_url": "https://davidchen.author.com"
    },
    {
        "name": "Maria Rodriguez",
        "contributor_type": "A01",
        "biography": "Maria Rodriguez writes historical fiction set in Latin America, drawing from her extensive research in colonial history.",
        "website_url": "https://mariarodriguez.net"
    },
    {
        "name": "James Thompson",
        "contributor_type": "A01",
        "biography": "James Thompson is a thriller writer known for fast-paced plots and complex mysteries.",
    },
    {
        "name": "Lisa Park",
        "contributor_type": "A01",
        "biography": "Lisa Park writes young adult fantasy novels that have captured readers worldwide.",
        "website_url": "https://lisapark.books.com"
    }
]

BOOKS = [
    {
        "title": "The Last Harbor",
        "isbn": "9780123456789",
        "subtitle": "A Maritime Mystery",
        "publication_date": "2024-03-15",
        "product_form": "BB"
    },
    {
        "title": "Neural Networks",
        "isbn": "9780123456790", 
        "subtitle": "A Science Fiction Thriller",
        "publication_date": "2024-06-20",
        "product_form": "BB"
    },
    {
        "title": "Gardens of Memory",
        "isbn": "9780123456791",
        "subtitle": "A Historical Romance",
        "publication_date": "2024-09-10",
        "product_form": "BB"
    },
    {
        "title": "The Silent Witness",
        "isbn": "9780123456792",
        "subtitle": "A Detective Novel",
        "publication_date": "2024-11-05",
        "product_form": "BB"
    },
    {
        "title": "Realm of Shadows",
        "isbn": "9780123456793",
        "subtitle": "Young Adult Fantasy",
        "publication_date": "2025-01-20",
        "product_form": "BB"
    },
    {
        "title": "Coastal Winds",
        "isbn": "9780123456794",
        "subtitle": "Contemporary Fiction",
        "publication_date": "2024-08-12",
        "product_form": "BC"
    }
]

CONTRACTS = [
    {
        "contract_name": "Amazon KDP Distribution Agreement",
        "contract_type": "distribution_agreement",
        "retailer": "amazon_kdp",
        "effective_date": str(date.today() - timedelta(days=90)),
        "territory_restrictions": ["US", "CA", "UK"],
        "validation_rules": {
            "required_fields": ["isbn", "title", "price"],
            "min_discount": 0.4,
            "max_price": 50.0
        }
    },
    {
        "contract_name": "Barnes & Noble Press Agreement",
        "contract_type": "distribution_agreement", 
        "retailer": "barnes_noble",
        "effective_date": str(date.today() - timedelta(days=60)),
        "territory_restrictions": ["US"],
        "validation_rules": {
            "required_fields": ["isbn", "title", "author", "price", "description"],
            "min_discount": 0.3,
            "max_price": 40.0
        }
    },
    {
        "contract_name": "Apple Books Partnership",
        "contract_type": "distribution_agreement",
        "retailer": "apple_books", 
        "effective_date": str(date.today() - timedelta(days=30)),
        "territory_restrictions": ["US", "CA", "UK", "AU"],
        "validation_rules": {
            "required_fields": ["isbn", "title", "author"],
            "min_discount": 0.3
        }
    }
]

def make_request(method: str, endpoint: str, data: dict = None) -> dict:
    """Make API request with error handling"""
    url = f"{BASE_URL}{endpoint}"
    
    try:
        if method == "POST":
            response = requests.post(url, headers=HEADERS, json=data)
        elif method == "GET":
            response = requests.get(url, headers=HEADERS)
        elif method == "PUT":
            response = requests.put(url, headers=HEADERS, json=data)
        else:
            raise ValueError(f"Unsupported method: {method}")
            
        if response.status_code in [200, 201]:
            return response.json()
        else:
            print(f"❌ Request failed: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Request error: {e}")
        return None

def create_publishers() -> List[Dict]:
    """Create sample publishers"""
    print("\n📚 Creating Publishers...")
    publishers = []
    
    for pub_data in PUBLISHERS:
        result = make_request("POST", "/publishers", pub_data)
        if result:
            publishers.append(result)
            print(f"✅ Created: {result['name']} (ID: {result['id'][:8]}...)")
        else:
            print(f"❌ Failed to create publisher: {pub_data['name']}")
    
    return publishers

def create_authors() -> List[Dict]:
    """Create sample authors"""
    print("\n✍️ Creating Authors...")
    authors = []
    
    for author_data in AUTHORS:
        result = make_request("POST", "/authors", author_data)
        if result:
            authors.append(result)
            print(f"✅ Created: {result['name']} (ID: {result['id'][:8]}...)")
        else:
            print(f"❌ Failed to create author: {author_data['name']}")
    
    return authors

def create_books_and_link_authors(publishers: List[Dict], authors: List[Dict]) -> List[Dict]:
    """Create sample books and link them to authors"""
    print("\n📖 Creating Books and Linking Authors...")
    books = []
    
    for i, book_data in enumerate(BOOKS):
        # Assign book to a publisher (round-robin)
        publisher = publishers[i % len(publishers)]
        book_data["publisher_id"] = publisher["id"]
        
        # Create book
        result = make_request("POST", "/books", book_data)
        if result:
            book_id = result["id"]
            books.append(result)
            print(f"✅ Created book: {result['title']} (ID: {book_id[:8]}...)")
            
            # Link author to book
            author = authors[i % len(authors)]
            link_data = [{
                "author_id": author["id"],
                "sequence_number": 1,
                "contributor_role": "A01"
            }]
            
            link_result = make_request("PUT", f"/books/{book_id}/authors", link_data)
            if link_result:
                print(f"✅ Linked author {author['name']} to {result['title']}")
            else:
                print(f"❌ Failed to link author to book: {result['title']}")
        else:
            print(f"❌ Failed to create book: {book_data['title']}")
    
    return books

def create_contracts(publishers: List[Dict]) -> List[Dict]:
    """Create sample contracts"""
    print("\n📄 Creating Contracts...")
    contracts = []
    
    for i, contract_data in enumerate(CONTRACTS):
        # Assign contract to a publisher (round-robin)
        publisher = publishers[i % len(publishers)]
        contract_data["publisher_id"] = publisher["id"]
        
        result = make_request("POST", "/contracts", contract_data)
        if result:
            contracts.append(result)
            print(f"✅ Created contract: {result['contract_name']} (ID: {result['id'][:8]}...)")
        else:
            print(f"❌ Failed to create contract: {contract_data['contract_name']}")
    
    return contracts

def check_compliance(books: List[Dict], contracts: List[Dict]):
    """Test compliance checking"""
    print("\n🔍 Testing Compliance Checks...")
    
    for book in books[:3]:  # Test first 3 books
        for contract in contracts[:2]:  # Against first 2 contracts
            if book["publisher_id"] == contract["publisher_id"]:
                endpoint = f"/books/{book['id']}/check-compliance?contract_id={contract['id']}"
                result = make_request("POST", endpoint)
                if result:
                    status = "✅" if result["compliant"] else "⚠️"
                    print(f"{status} {book['title'][:20]} vs {contract['contract_name'][:20]}: {result['status']}")

def display_summary(publishers: List[Dict], authors: List[Dict], books: List[Dict], contracts: List[Dict]):
    """Display generation summary"""
    print("\n" + "="*60)
    print("🎉 SAMPLE DATA GENERATION COMPLETE!")
    print("="*60)
    print(f"📚 Publishers created: {len(publishers)}")
    print(f"✍️ Authors created: {len(authors)}")
    print(f"📖 Books created: {len(books)}")
    print(f"📄 Contracts created: {len(contracts)}")
    
    print(f"\n🌐 API Server: {BASE_URL}")
    print("📊 Publisher Dashboards:")
    for pub in publishers:
        print(f"   • {pub['name']}: GET /publishers/{pub['id']}/dashboard")
    
    print("\n🔍 Test Endpoints:")
    print(f"   • Search authors: GET /authors/search?q=Sarah")
    print(f"   • Book details: GET /books/{books[0]['id'] if books else 'BOOK_ID'}")
    print("   • Health check: GET /health")

def main():
    """Generate all sample data"""
    print("🚀 METAOPS SAMPLE DATA GENERATOR")
    print("="*60)
    
    # Check API health
    health = make_request("GET", "/health")
    if not health:
        print("❌ API not available. Make sure the server is running on port 8002")
        return
    
    print(f"✅ API is healthy - {health.get('status', 'unknown')}")
    
    # Generate data in sequence
    publishers = create_publishers()
    if not publishers:
        print("❌ Cannot continue without publishers")
        return
        
    authors = create_authors()
    if not authors:
        print("❌ Cannot continue without authors")
        return
    
    books = create_books_and_link_authors(publishers, authors)
    contracts = create_contracts(publishers)
    
    # Test compliance
    if books and contracts:
        check_compliance(books, contracts)
    
    # Show summary
    display_summary(publishers, authors, books, contracts)

if __name__ == "__main__":
    main()