#!/usr/bin/env python3
"""
Reality Check: Actually test what users see in the UI
This tests the UI components, not just API endpoints
"""
import requests
import time
from pathlib import Path

# Test URLs
API_URL = "http://100.111.114.84:8002/api/v1"
UI_URL = "http://100.111.114.84:8003"

def test_ui_loads():
    """Test if UI actually loads and shows content"""
    print("🌐 Testing UI Reality...")
    
    try:
        response = requests.get(UI_URL, timeout=10)
        if response.status_code != 200:
            print(f"❌ UI not loading: Status {response.status_code}")
            return False
            
        html = response.text
        
        # Check for key UI elements
        checks = [
            ("Streamlit app", "streamlit" in html.lower()),
            ("MetaOps title", "metaops" in html.lower()),
            ("Publisher selection", "publisher" in html.lower()),
            ("No error messages", "error" not in html.lower())
        ]
        
        for check_name, passed in checks:
            status = "✅" if passed else "❌"
            print(f"   {status} {check_name}")
            
        return all(passed for _, passed in checks)
        
    except Exception as e:
        print(f"❌ UI test failed: {e}")
        return False

def test_dashboard_data_flow():
    """Test if dashboard actually shows data to users"""
    print("\n📊 Testing Dashboard Data Flow...")
    
    auth_headers = {
        "Authorization": "Bearer demo.eyJ1c2VyX2lkIjoiZGVtb191c2VyIn0.signature",
        "Content-Type": "application/json"
    }
    
    try:
        # Get publisher
        pubs = requests.get(f"{API_URL}/publishers", headers=auth_headers).json()
        if not pubs:
            print("❌ No publishers found")
            return False
            
        pub_id = pubs[0]['id']
        print(f"   Testing publisher: {pubs[0]['name']}")
        
        # Get dashboard data
        dashboard = requests.get(f"{API_URL}/publishers/{pub_id}/dashboard", headers=auth_headers).json()
        
        # Check if dashboard has meaningful data
        metrics = dashboard.get('metrics', {})
        book_count = metrics.get('book_count', 0)
        contract_count = metrics.get('contract_count', 0)
        recent_books = dashboard.get('recent_books', [])
        
        print(f"   Books: {book_count}")
        print(f"   Contracts: {contract_count}")
        print(f"   Recent books: {len(recent_books)}")
        
        if book_count == 0:
            print("❌ Dashboard shows no books - looks blank to users")
            return False
            
        if contract_count == 0:
            print("❌ Dashboard shows no contracts - missing key functionality")
            return False
            
        if not recent_books:
            print("❌ No recent books shown - empty recent activity")
            return False
            
        print("✅ Dashboard has meaningful data")
        return True
        
    except Exception as e:
        print(f"❌ Dashboard test failed: {e}")
        return False

def test_onix_namespace_compliance():
    """Test if ONIX actually has proper namespaces as per CLAUDE.md requirements"""
    print("\n📋 Testing ONIX Namespace Compliance...")
    
    auth_headers = {
        "Authorization": "Bearer demo.eyJ1c2VyX2lkIjoiZGVtb191c2VyIn0.signature",
        "Content-Type": "application/json"
    }
    
    try:
        # Get a book
        books = requests.get(f"{API_URL}/books", headers=auth_headers).json()
        if not books:
            print("❌ No books available for ONIX testing")
            return False
            
        book_id = books[0]['id']
        print(f"   Testing ONIX for: {books[0]['title']}")
        
        # Generate ONIX
        onix_result = requests.get(f"{API_URL}/books/{book_id}/onix", headers=auth_headers).json()
        xml = onix_result.get('onix_xml', '')
        
        if not xml:
            print("❌ No ONIX XML generated")
            return False
            
        # Check namespace requirements from CLAUDE.md
        namespace_checks = [
            ("Has namespace declaration", 'xmlns=' in xml),
            ("Uses EDItEUR namespace", 'ns.editeur.org/onix/3.0/reference' in xml),
            ("Proper ONIX root", 'ONIXMessage' in xml),
            ("Has release version", 'release=' in xml)
        ]
        
        all_passed = True
        for check_name, passed in namespace_checks:
            status = "✅" if passed else "❌"
            print(f"   {status} {check_name}")
            if not passed:
                all_passed = False
                
        if all_passed:
            print("✅ ONIX namespace compliance verified")
        else:
            print("❌ ONIX namespace compliance failed")
            
        return all_passed
        
    except Exception as e:
        print(f"❌ ONIX namespace test failed: {e}")
        return False

def test_contract_functionality():
    """Test if contract management actually works"""
    print("\n📄 Testing Contract Functionality...")
    
    auth_headers = {
        "Authorization": "Bearer demo.eyJ1c2VyX2lkIjoiZGVtb191c2VyIn0.signature",
        "Content-Type": "application/json"
    }
    
    try:
        # Get publishers and contracts
        pubs = requests.get(f"{API_URL}/publishers", headers=auth_headers).json()
        if not pubs:
            print("❌ No publishers for contract testing")
            return False
            
        pub_id = pubs[0]['id']
        contracts = requests.get(f"{API_URL}/contracts?publisher_id={pub_id}", headers=auth_headers).json()
        
        if not contracts:
            print("❌ No contracts found - contract management appears non-functional")
            return False
            
        print(f"   Found {len(contracts)} contracts")
        
        # Test compliance checking
        books = requests.get(f"{API_URL}/books?publisher_id={pub_id}", headers=auth_headers).json()
        if books and contracts:
            book_id = books[0]['id']
            contract_id = contracts[0]['id']
            
            compliance = requests.post(
                f"{API_URL}/books/{book_id}/check-compliance",
                headers=auth_headers,
                params={"contract_id": contract_id}
            )
            
            if compliance.status_code == 200:
                result = compliance.json()
                print(f"   Compliance check: {result.get('status', 'unknown')}")
                print("✅ Contract functionality verified")
                return True
            else:
                print("❌ Contract compliance checking failed")
                return False
        else:
            print("❌ Insufficient data for contract testing")
            return False
            
    except Exception as e:
        print(f"❌ Contract functionality test failed: {e}")
        return False

def main():
    """Run reality check tests"""
    print("🔍 METAOPS REALITY CHECK")
    print("Testing what users actually see vs. what APIs return")
    print("=" * 60)
    
    tests = [
        ("UI Loads and Shows Content", test_ui_loads),
        ("Dashboard Shows Meaningful Data", test_dashboard_data_flow),
        ("ONIX Namespace Compliance", test_onix_namespace_compliance),
        ("Contract Management Works", test_contract_functionality)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n🧪 {test_name}")
        print("-" * 50)
        result = test_func()
        results.append((test_name, result))
    
    # Summary
    print("\n" + "=" * 60)
    print("🎯 REALITY CHECK RESULTS")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 System appears to work as users would expect")
    else:
        print("⚠️  System has user-facing issues that need attention")
        print("\n🔧 ISSUES TO FIX:")
        for test_name, result in results:
            if not result:
                print(f"   • {test_name}")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)