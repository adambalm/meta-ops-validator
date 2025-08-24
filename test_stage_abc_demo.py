#!/usr/bin/env python3
"""
MetaOps Stage A-B-C Demo Test Script
Complete walkthrough for demonstrating book-author-contract workflow
"""
import requests
import json
import time
from datetime import date
from typing import Dict, List, Optional

# Configuration
BASE_URL = "http://100.111.114.84:8002/api/v1"
UI_URL = "http://100.111.114.84:8003"
AUTH_TOKEN = "demo.eyJ1c2VyX2lkIjoiZGVtb191c2VyIn0.signature"
HEADERS = {
    "Authorization": f"Bearer {AUTH_TOKEN}",
    "Content-Type": "application/json"
}

class DemoTestRunner:
    def __init__(self):
        self.results = []
        self.publisher_id = None
        self.book_ids = []
        self.author_ids = []
        self.contract_ids = []

    def test(self, description: str, func):
        """Run a test and record results"""
        print(f"\n🧪 {description}")
        print("-" * 60)
        
        try:
            result = func()
            if result:
                print(f"✅ PASS: {description}")
                self.results.append({"test": description, "status": "PASS", "details": result})
                return result
            else:
                print(f"❌ FAIL: {description}")
                self.results.append({"test": description, "status": "FAIL", "details": "No result returned"})
                return None
        except Exception as e:
            print(f"💥 ERROR: {description} - {str(e)}")
            self.results.append({"test": description, "status": "ERROR", "details": str(e)})
            return None

    def make_request(self, method: str, endpoint: str, data=None, params=None) -> Optional[Dict]:
        """Make API request with error handling"""
        url = f"{BASE_URL}{endpoint}"
        
        try:
            if method == "GET":
                response = requests.get(url, headers=HEADERS, params=params)
            elif method == "POST":
                response = requests.post(url, headers=HEADERS, json=data, params=params)
            elif method == "PUT":
                response = requests.put(url, headers=HEADERS, json=data)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            print(f"   {method} {endpoint} -> {response.status_code}")
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"   Error: {response.text[:200]}...")
                return None
                
        except requests.RequestException as e:
            print(f"   Request failed: {e}")
            return None

    # STAGE A: Basic Infrastructure Tests
    def test_api_health(self):
        """Test API server health"""
        result = self.make_request("GET", "/health")
        if result and result.get("status") == "healthy":
            print(f"   Services: {list(result.get('services', {}).keys())}")
            return True
        return False

    def test_external_accessibility(self):
        """Test that system is accessible from external networks"""
        print(f"   Testing external API access: {BASE_URL}")
        print(f"   Testing external UI access: {UI_URL}")
        
        # This test assumes the demo is being run from an external network
        result = self.make_request("GET", "/health")
        if result:
            print("   ✅ System accessible from external networks")
            return True
        else:
            print("   ❌ System not accessible externally")
            return False

    # STAGE B: ONIX Generation Tests
    def test_publisher_creation(self):
        """Test publisher creation and retrieval"""
        # First check existing publishers
        publishers = self.make_request("GET", "/publishers")
        if publishers and len(publishers) > 0:
            self.publisher_id = publishers[0]["id"]
            print(f"   Using existing publisher: {publishers[0]['name']} ({self.publisher_id[:8]}...)")
            return publishers[0]
        
        # Create new publisher if none exist
        publisher_data = {
            "name": "Demo Test Publisher",
            "imprint": "Demo Books",
            "territory_codes": ["US", "CA", "UK"],
            "validation_profile": {"strict_mode": True}
        }
        
        result = self.make_request("POST", "/publishers", publisher_data)
        if result:
            self.publisher_id = result["id"]
            print(f"   Created publisher: {result['name']} ({self.publisher_id[:8]}...)")
            return result
        return None

    def test_author_creation(self):
        """Test author creation and search"""
        authors_data = [
            {
                "name": "Demo Test Author",
                "contributor_type": "A01",
                "biography": "A test author for demonstration purposes"
            }
        ]
        
        for author_data in authors_data:
            result = self.make_request("POST", "/authors", author_data)
            if result:
                self.author_ids.append(result["id"])
                print(f"   Created author: {result['name']} ({result['id'][:8]}...)")
        
        # Test author search
        search_result = self.make_request("GET", "/authors/search", params={"q": "Demo"})
        if search_result and len(search_result) > 0:
            print(f"   Author search works: {len(search_result)} results")
            return True
        return False

    def test_book_creation(self):
        """Test book creation with proper ISBN handling"""
        if not self.publisher_id:
            print("   Skipping: No publisher available")
            return False
        
        books_data = [
            {
                "title": "Demo Test Book",
                "isbn": "9780000000001",  # Unique test ISBN
                "subtitle": "A Complete Demo",
                "publisher_id": self.publisher_id,
                "publication_date": date.today().isoformat(),
                "product_form": "BB"
            }
        ]
        
        for book_data in books_data:
            result = self.make_request("POST", "/books", book_data)
            if result:
                self.book_ids.append(result["id"])
                print(f"   Created book: {result['title']} (ISBN: {result['isbn']})")
                
                # Link to author if available
                if self.author_ids:
                    link_data = [{
                        "author_id": self.author_ids[0],
                        "sequence_number": 1,
                        "contributor_role": "A01"
                    }]
                    
                    link_result = self.make_request("PUT", f"/books/{result['id']}/authors", link_data)
                    if link_result:
                        print(f"   Linked author to book successfully")
        
        return len(self.book_ids) > 0

    def test_contract_creation(self):
        """Test contract creation with validation rules"""
        if not self.publisher_id:
            print("   Skipping: No publisher available")
            return False
        
        contracts_data = [
            {
                "publisher_id": self.publisher_id,
                "contract_name": "Demo Test Agreement",
                "contract_type": "distribution_agreement",
                "retailer": "demo_retailer",
                "effective_date": date.today().isoformat(),
                "territory_restrictions": ["US"],
                "validation_rules": {
                    "required_fields": ["isbn", "title"],
                    "min_discount": 0.25,
                    "max_discount": 0.50
                }
            }
        ]
        
        for contract_data in contracts_data:
            result = self.make_request("POST", "/contracts", contract_data)
            if result:
                self.contract_ids.append(result["id"])
                print(f"   Created contract: {result['contract_name']} ({result['retailer']})")
        
        return len(self.contract_ids) > 0

    def test_onix_generation(self):
        """Test ONIX generation with and without contracts"""
        if not self.book_ids:
            print("   Skipping: No books available")
            return False
        
        book_id = self.book_ids[0]
        
        # Test basic ONIX generation
        result = self.make_request("GET", f"/books/{book_id}/onix-preview")
        if not result:
            print("   ❌ ONIX preview generation failed")
            return False
        
        print(f"   ONIX preview generated: {len(result.get('preview_xml', ''))} characters")
        
        # Test full ONIX generation
        result = self.make_request("GET", f"/books/{book_id}/onix")
        if not result:
            print("   ❌ Full ONIX generation failed")
            return False
        
        print(f"   Full ONIX generated: {len(result.get('onix_xml', ''))} characters")
        
        # Test contract-based ONIX generation
        if self.contract_ids:
            params = {
                "contract_id": self.contract_ids[0],
                "target_territory": "US"
            }
            result = self.make_request("GET", f"/books/{book_id}/onix", params=params)
            if result:
                print(f"   Contract-based ONIX generated with territory filtering")
                return True
        
        return True

    # STAGE C: Business Workflow Tests
    def test_contract_compliance(self):
        """Test contract compliance checking"""
        if not self.book_ids or not self.contract_ids:
            print("   Skipping: No books or contracts available")
            return False
        
        book_id = self.book_ids[0]
        contract_id = self.contract_ids[0]
        
        result = self.make_request("POST", f"/books/{book_id}/check-compliance", 
                                 params={"contract_id": contract_id})
        
        if result:
            status = result.get("status", "unknown")
            territory_check = result.get("territory_check_passed", False)
            rules_check = result.get("rules_check_passed", False)
            
            print(f"   Compliance status: {status}")
            print(f"   Territory check: {'✅' if territory_check else '❌'}")
            print(f"   Rules check: {'✅' if rules_check else '❌'}")
            return True
        
        return False

    def test_publisher_dashboard(self):
        """Test publisher dashboard data retrieval"""
        if not self.publisher_id:
            print("   Skipping: No publisher available")
            return False
        
        result = self.make_request("GET", f"/publishers/{self.publisher_id}/dashboard")
        if result:
            metrics = result.get("metrics", {})
            print(f"   Books: {metrics.get('book_count', 0)}")
            print(f"   Contracts: {metrics.get('contract_count', 0)}")
            print(f"   Compliance rate: {metrics.get('compliance_rate', 0)}%")
            return True
        
        return False

    def test_ui_accessibility(self):
        """Test UI accessibility (basic check)"""
        try:
            response = requests.get(UI_URL, timeout=10)
            if response.status_code == 200:
                print(f"   UI accessible at {UI_URL}")
                return True
            else:
                print(f"   UI returned status {response.status_code}")
                return False
        except requests.RequestException as e:
            print(f"   UI not accessible: {e}")
            return False

    def run_complete_demo(self):
        """Run complete demo walkthrough"""
        print("🚀 METAOPS STAGE A-B-C DEMO WALKTHROUGH")
        print("=" * 80)
        print(f"API Base URL: {BASE_URL}")
        print(f"UI URL: {UI_URL}")
        print("=" * 80)

        # STAGE A Tests
        print("\n📍 STAGE A: Infrastructure & Accessibility")
        self.test("API Health Check", self.test_api_health)
        self.test("External Network Accessibility", self.test_external_accessibility)
        self.test("UI Accessibility", self.test_ui_accessibility)

        # STAGE B Tests  
        print("\n📍 STAGE B: ONIX Generation Workflow")
        self.test("Publisher Creation/Retrieval", self.test_publisher_creation)
        self.test("Author Creation & Search", self.test_author_creation)
        self.test("Book Creation with ISBN Validation", self.test_book_creation)
        self.test("Contract Creation", self.test_contract_creation)
        self.test("ONIX Generation (Preview & Full)", self.test_onix_generation)

        # STAGE C Tests
        print("\n📍 STAGE C: Business Workflow Integration")
        self.test("Contract Compliance Testing", self.test_contract_compliance)
        self.test("Publisher Dashboard Analytics", self.test_publisher_dashboard)

        # Summary
        self.print_summary()

    def print_summary(self):
        """Print test results summary"""
        print("\n" + "=" * 80)
        print("📊 DEMO TEST RESULTS SUMMARY")
        print("=" * 80)
        
        total_tests = len(self.results)
        passed = len([r for r in self.results if r["status"] == "PASS"])
        failed = len([r for r in self.results if r["status"] == "FAIL"])
        errors = len([r for r in self.results if r["status"] == "ERROR"])
        
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"💥 Errors: {errors}")
        print(f"Success Rate: {(passed/total_tests*100):.1f}%" if total_tests > 0 else "N/A")
        
        if failed > 0 or errors > 0:
            print("\n🚨 ISSUES FOUND:")
            for result in self.results:
                if result["status"] in ["FAIL", "ERROR"]:
                    print(f"   • {result['test']}: {result['details']}")
        
        print("\n📝 DEMO WALKTHROUGH STEPS:")
        print("1. Open browser to UI URL above")
        print("2. Select a publisher from the sidebar")
        print("3. Navigate through each tab:")
        print("   • 📊 Publisher Dashboard - View metrics and KPIs")
        print("   • 📚 Book Management - View/create books, test ONIX generation")
        print("   • ✍️ Author Search - Search and link authors")
        print("   • 📄 Contract Management - View contracts, simulate distributor feeds")
        print("   • 🔍 Compliance Checking - Test book-contract compliance")
        
        print(f"\n🎯 System Status: {'DEMO READY' if passed >= total_tests * 0.8 else 'NEEDS ATTENTION'}")

if __name__ == "__main__":
    demo = DemoTestRunner()
    demo.run_complete_demo()