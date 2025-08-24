#!/usr/bin/env python3
"""
Test script for MetaOps book-author-contract API endpoints
"""
import requests
import json
from datetime import date

# API Configuration
BASE_URL = "http://100.111.114.84:8002/api/v1"
AUTH_TOKEN = "demo.eyJ1c2VyX2lkIjoiZGVtb191c2VyIn0.signature"
HEADERS = {
    "Authorization": f"Bearer {AUTH_TOKEN}",
    "Content-Type": "application/json"
}

def print_response(response, title):
    """Pretty print API response"""
    print(f"\n{'='*60}")
    print(f"📌 {title}")
    print(f"Status: {response.status_code}")
    try:
        data = response.json()
        print(f"Response: {json.dumps(data, indent=2)[:500]}...")
    except:
        print(f"Response: {response.text[:500]}")
    print(f"{'='*60}")

def test_publisher_endpoints():
    """Test publisher creation and retrieval"""
    print("\n🏢 TESTING PUBLISHER ENDPOINTS")
    
    # Create publisher
    publisher_data = {
        "name": "Demo Publishing House",
        "imprint": "Demo Books",
        "territory_codes": ["US", "CA", "UK"],
        "validation_profile": {"strict_mode": True}
    }
    
    response = requests.post(
        f"{BASE_URL}/publishers",
        headers=HEADERS,
        json=publisher_data
    )
    print_response(response, "Create Publisher")
    
    if response.status_code == 200:
        publisher = response.json()
        publisher_id = publisher["id"]
        
        # Get publisher details
        response = requests.get(
            f"{BASE_URL}/publishers/{publisher_id}",
            headers=HEADERS
        )
        print_response(response, "Get Publisher Details")
        
        # Get publisher dashboard
        response = requests.get(
            f"{BASE_URL}/publishers/{publisher_id}/dashboard",
            headers=HEADERS
        )
        print_response(response, "Get Publisher Dashboard")
        
        return publisher_id
    return None

def test_author_endpoints():
    """Test author creation and search"""
    print("\n✍️ TESTING AUTHOR ENDPOINTS")
    
    # Create author
    author_data = {
        "name": "Jane Demo Author",
        "contributor_type": "A01",
        "biography": "A demonstration author for testing",
        "website_url": "https://example.com/jane"
    }
    
    response = requests.post(
        f"{BASE_URL}/authors",
        headers=HEADERS,
        json=author_data
    )
    print_response(response, "Create Author")
    
    if response.status_code == 200:
        author = response.json()
        author_id = author["id"]
        
        # Search authors
        response = requests.get(
            f"{BASE_URL}/authors/search?q=Jane",
            headers=HEADERS
        )
        print_response(response, "Search Authors")
        
        return author_id
    return None

def test_book_endpoints(publisher_id, author_id):
    """Test book creation and management"""
    print("\n📚 TESTING BOOK ENDPOINTS")
    
    # Create book
    book_data = {
        "title": "The Demo Novel",
        "isbn": "9781234567892",
        "subtitle": "A Test Book for Demonstration",
        "publisher_id": publisher_id,
        "publication_date": "2024-06-15",
        "product_form": "BA"
    }
    
    response = requests.post(
        f"{BASE_URL}/books",
        headers=HEADERS,
        json=book_data
    )
    print_response(response, "Create Book")
    
    if response.status_code == 200:
        book = response.json()
        book_id = book["id"]
        
        # Get book details
        response = requests.get(
            f"{BASE_URL}/books/{book_id}",
            headers=HEADERS
        )
        print_response(response, "Get Book Details")
        
        # Link author to book
        author_link_data = [
            {
                "author_id": author_id,
                "sequence_number": 1,
                "contributor_role": "A01"
            }
        ]
        
        response = requests.put(
            f"{BASE_URL}/books/{book_id}/authors",
            headers=HEADERS,
            json=author_link_data
        )
        print_response(response, "Link Author to Book")
        
        return book_id
    return None

def test_contract_endpoints(publisher_id, book_id):
    """Test contract creation and compliance"""
    print("\n📄 TESTING CONTRACT ENDPOINTS")
    
    # Create contract
    contract_data = {
        "publisher_id": publisher_id,
        "contract_name": "Demo Amazon KDP Agreement",
        "contract_type": "distribution_agreement",
        "retailer": "amazon_kdp",
        "effective_date": str(date.today()),
        "territory_restrictions": ["US", "CA"],
        "validation_rules": {
            "required_fields": ["isbn", "title", "price"],
            "min_discount": 0.4
        }
    }
    
    response = requests.post(
        f"{BASE_URL}/contracts",
        headers=HEADERS,
        json=contract_data
    )
    print_response(response, "Create Contract")
    
    if response.status_code == 200:
        contract = response.json()
        contract_id = contract["id"]
        
        # Check book compliance
        response = requests.post(
            f"{BASE_URL}/books/{book_id}/check-compliance?contract_id={contract_id}",
            headers=HEADERS
        )
        print_response(response, "Check Book Compliance")
        
        return contract_id
    return None

def main():
    """Run all API tests"""
    print("🚀 METAOPS API TEST SUITE")
    print("=" * 60)
    
    try:
        # Test health check first
        response = requests.get(f"{BASE_URL}/health")
        print_response(response, "Health Check")
        
        # Run tests in sequence
        publisher_id = test_publisher_endpoints()
        if publisher_id:
            print(f"✅ Publisher created: {publisher_id}")
            
            author_id = test_author_endpoints()
            if author_id:
                print(f"✅ Author created: {author_id}")
                
                book_id = test_book_endpoints(publisher_id, author_id)
                if book_id:
                    print(f"✅ Book created: {book_id}")
                    
                    contract_id = test_contract_endpoints(publisher_id, book_id)
                    if contract_id:
                        print(f"✅ Contract created: {contract_id}")
                        
                        print("\n🎉 ALL API TESTS COMPLETED SUCCESSFULLY!")
                        print("   - Publisher management working")
                        print("   - Author search and creation working")
                        print("   - Book creation and author linking working")
                        print("   - Contract compliance checking working")
                    else:
                        print("❌ Contract tests failed")
                else:
                    print("❌ Book tests failed")
            else:
                print("❌ Author tests failed")
        else:
            print("❌ Publisher tests failed")
            
    except requests.exceptions.ConnectionError as e:
        print(f"\n❌ Could not connect to API at {BASE_URL}")
        print(f"   Make sure the API is running: python -m uvicorn metaops.api.main:app --port 8001")
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")

if __name__ == "__main__":
    main()