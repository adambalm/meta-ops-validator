#!/usr/bin/env python3
"""
Quick test script to verify the EDItEUR ONIX Codelists XML files are valid and parseable.
"""

import xml.etree.ElementTree as ET
import os

def test_xml_codelists():
    """Test loading and parsing the ONIX codelists XML file."""
    codelist_file = '/home/ed/meta-ops-validator/data/editeur/codelists/ONIX_BookProduct_Codelists_Issue_70.xml'
    
    if not os.path.exists(codelist_file):
        print(f"❌ Codelist file not found: {codelist_file}")
        return False
    
    print(f"📁 Found codelist file: {codelist_file}")
    print(f"📊 File size: {os.path.getsize(codelist_file):,} bytes")
    
    try:
        # Parse the XML
        tree = ET.parse(codelist_file)
        root = tree.getroot()
        print(f"✅ XML parsed successfully")
        print(f"🏷️  Root element: {root.tag}")
        
        # Get issue number
        issue_num = root.find('IssueNumber')
        if issue_num is not None:
            print(f"📋 Issue number: {issue_num.text}")
        
        # Count codelists
        codelists = root.findall('CodeList')
        print(f"📝 Number of codelists: {len(codelists)}")
        
        # Show a few examples
        print("\n🔍 Sample codelists:")
        for i, codelist in enumerate(codelists[:5]):
            list_num = codelist.find('CodeListNumber')
            list_desc = codelist.find('CodeListDescription')
            codes = codelist.findall('Code')
            
            if list_num is not None and list_desc is not None:
                print(f"  List {list_num.text}: {list_desc.text} ({len(codes)} codes)")
        
        # Test specific important codelists
        print("\n🎯 Testing key codelists:")
        
        # Product form codes (List 150)
        product_forms = []
        for codelist in codelists:
            list_num = codelist.find('CodeListNumber')
            if list_num is not None and list_num.text == '150':
                codes = codelist.findall('Code')
                for code in codes[:3]:  # Just first 3
                    code_value = code.find('CodeValue')
                    code_desc = code.find('CodeDescription')
                    if code_value is not None and code_desc is not None:
                        product_forms.append((code_value.text, code_desc.text))
                break
        
        if product_forms:
            print(f"  📚 Product form codes (List 150): Found {len(product_forms)} sample codes")
            for code_val, code_desc in product_forms:
                print(f"    {code_val}: {code_desc}")
        else:
            print("  ❌ Product form codes (List 150) not found")
        
        print(f"\n✅ Codelist validation completed successfully!")
        return True
        
    except ET.ParseError as e:
        print(f"❌ XML parsing error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    test_xml_codelists()