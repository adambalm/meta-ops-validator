#!/usr/bin/env python3
"""
Generate test ONIX files with varying completeness levels
"""

import xml.etree.ElementTree as ET
from pathlib import Path
import random
from datetime import datetime, timedelta

def create_onix_file(completeness_level: str, filename: str, use_namespace: bool = True):
    """Create ONIX file with specified completeness level."""
    
    # Namespace setup
    if use_namespace:
        root_attrs = {
            'xmlns': 'http://ns.editeur.org/onix/3.0/reference',
            'release': '3.0'
        }
        ns = '{http://ns.editeur.org/onix/3.0/reference}'
    else:
        root_attrs = {'release': '3.0'}
        ns = ''
    
    # Create root element
    root = ET.Element(f'{ns}ONIXMessage', root_attrs)
    
    # Header
    header = ET.SubElement(root, f'{ns}Header')
    ET.SubElement(header, f'{ns}Sender').text = 'MetaOps Test Generator'
    ET.SubElement(header, f'{ns}SentDateTime').text = datetime.now().strftime('%Y%m%dT%H%M%S')
    ET.SubElement(header, f'{ns}MessageNote').text = f'Test file - {completeness_level} completeness'
    
    # Product
    product = ET.SubElement(root, f'{ns}Product')
    
    # Record reference
    ET.SubElement(product, f'{ns}RecordReference').text = f'TEST_{completeness_level.upper()}_{random.randint(1000, 9999)}'
    
    # Notification type
    ET.SubElement(product, f'{ns}NotificationType').text = '03'  # Early notification
    
    # Always include basic structure
    descriptive_detail = ET.SubElement(product, f'{ns}DescriptiveDetail')
    publishing_detail = ET.SubElement(product, f'{ns}PublishingDetail')
    product_supply = ET.SubElement(product, f'{ns}ProductSupply')
    
    # Completeness-based content
    if completeness_level == 'minimal':
        # Just the bare minimum
        _add_product_form(descriptive_detail, ns, 'BC')  # Book
        
    elif completeness_level == 'basic':
        # Core fields for basic validation
        _add_isbn(product, ns, '9781234567890')
        _add_title(descriptive_detail, ns, 'Test Book Title')
        _add_contributor(descriptive_detail, ns, 'Test Author')
        _add_product_form(descriptive_detail, ns, 'BC')
        _add_price(product_supply, ns, '19.99')
        
    elif completeness_level == 'good':
        # Nielsen target level (75%+)
        _add_isbn(product, ns, '9781234567890')
        _add_title(descriptive_detail, ns, 'Complete Test Book: A Comprehensive Guide')
        _add_contributor(descriptive_detail, ns, 'Dr. Jane Smith')
        _add_product_form(descriptive_detail, ns, 'BC')
        _add_description(descriptive_detail, ns, 'This is a comprehensive test book designed to validate ONIX metadata completeness scoring. It includes all major metadata fields required by modern retailers and discovery systems.')
        _add_subjects(descriptive_detail, ns, ['FIC000000', 'FIC019000'])  # Fiction/Literary
        _add_publisher(publishing_detail, ns, 'Test Publishing House')
        _add_publication_date(publishing_detail, ns, '20241201')
        _add_price(product_supply, ns, '24.99')
        
    elif completeness_level == 'excellent':
        # Maximum completeness (90%+)
        _add_isbn(product, ns, '9781234567890')
        _add_title(descriptive_detail, ns, 'The Complete Test Book: Advanced Metadata Validation Techniques')
        _add_contributor(descriptive_detail, ns, 'Dr. Jane Smith', '01')  # Author
        _add_contributor(descriptive_detail, ns, 'Prof. John Doe', '10')  # Editor
        _add_product_form(descriptive_detail, ns, 'BC')
        _add_description(descriptive_detail, ns, 'This comprehensive test book serves as the definitive guide to ONIX metadata validation and completeness scoring. Featuring detailed examples, best practices, and real-world case studies, it provides publishers with the knowledge needed to optimize their metadata for maximum sales impact across all retail channels.')
        _add_subjects(descriptive_detail, ns, ['COM018000', 'COM051380', 'BUS107000'])  # Computers/Data Processing
        _add_publisher(publishing_detail, ns, 'Advanced Publishing Solutions')
        _add_imprint(publishing_detail, ns, 'TechBook Imprint')
        _add_publication_date(publishing_detail, ns, '20241215')
        _add_series(descriptive_detail, ns, 'Metadata Management Series', '1')
        _add_price(product_supply, ns, '34.99')
        _add_cover_image(descriptive_detail, ns, 'https://example.com/covers/test-book-cover.jpg')
        
    elif completeness_level == 'problematic':
        # Designed to trigger validation errors
        _add_isbn(product, ns, '123456789')  # Invalid ISBN format
        _add_title(descriptive_detail, ns, 'X')  # Too short
        _add_product_form(descriptive_detail, ns, 'AB')  # Audio format (triggers demo rule)
        # Missing critical fields intentionally
        
    # Write file
    tree = ET.ElementTree(root)
    ET.indent(tree, space="  ", level=0)  # Pretty print
    
    output_path = Path(filename)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'wb') as f:
        tree.write(f, encoding='utf-8', xml_declaration=True)
    
    print(f"Created {completeness_level} ONIX file: {filename}")

def _add_isbn(product, ns: str, isbn: str):
    """Add ISBN identifier."""
    identifier = ET.SubElement(product, f'{ns}ProductIdentifier')
    ET.SubElement(identifier, f'{ns}ProductIDType').text = '15'  # ISBN-13
    ET.SubElement(identifier, f'{ns}IDValue').text = isbn

def _add_title(descriptive_detail, ns: str, title: str):
    """Add title information."""
    title_detail = ET.SubElement(descriptive_detail, f'{ns}TitleDetail')
    ET.SubElement(title_detail, f'{ns}TitleType').text = '01'  # Distinctive title
    title_element = ET.SubElement(title_detail, f'{ns}TitleElement')
    ET.SubElement(title_element, f'{ns}TitleElementLevel').text = '01'  # Product level
    ET.SubElement(title_element, f'{ns}TitleText').text = title

def _add_contributor(descriptive_detail, ns: str, name: str, role: str = '01'):
    """Add contributor (author, editor, etc.)."""
    contributor = ET.SubElement(descriptive_detail, f'{ns}Contributor')
    ET.SubElement(contributor, f'{ns}SequenceNumber').text = '1'
    ET.SubElement(contributor, f'{ns}ContributorRole').text = role
    ET.SubElement(contributor, f'{ns}PersonName').text = name

def _add_product_form(descriptive_detail, ns: str, form_code: str):
    """Add product form."""
    ET.SubElement(descriptive_detail, f'{ns}ProductForm').text = form_code

def _add_description(descriptive_detail, ns: str, text: str):
    """Add description text."""
    text_content = ET.SubElement(descriptive_detail, f'{ns}TextContent')
    ET.SubElement(text_content, f'{ns}TextType').text = '03'  # Main description
    ET.SubElement(text_content, f'{ns}Text').text = text

def _add_subjects(descriptive_detail, ns: str, codes: list):
    """Add subject classifications."""
    for code in codes:
        subject = ET.SubElement(descriptive_detail, f'{ns}Subject')
        ET.SubElement(subject, f'{ns}SubjectSchemeIdentifier').text = '10'  # BISAC
        ET.SubElement(subject, f'{ns}SubjectCode').text = code

def _add_publisher(publishing_detail, ns: str, name: str):
    """Add publisher information."""
    publisher = ET.SubElement(publishing_detail, f'{ns}Publisher')
    ET.SubElement(publisher, f'{ns}PublishingRole').text = '01'  # Publisher
    ET.SubElement(publisher, f'{ns}PublisherName').text = name

def _add_imprint(publishing_detail, ns: str, name: str):
    """Add imprint information."""
    imprint = ET.SubElement(publishing_detail, f'{ns}Imprint')
    ET.SubElement(imprint, f'{ns}ImprintName').text = name

def _add_publication_date(publishing_detail, ns: str, date: str):
    """Add publication date."""
    pub_date = ET.SubElement(publishing_detail, f'{ns}PublishingDate')
    ET.SubElement(pub_date, f'{ns}PublishingDateRole').text = '01'  # Publication date
    ET.SubElement(pub_date, f'{ns}Date').text = date

def _add_series(descriptive_detail, ns: str, series_name: str, number: str):
    """Add series information."""
    collection = ET.SubElement(descriptive_detail, f'{ns}Collection')
    ET.SubElement(collection, f'{ns}CollectionType').text = '10'  # Series
    title_detail = ET.SubElement(collection, f'{ns}TitleDetail')
    ET.SubElement(title_detail, f'{ns}TitleType').text = '01'
    title_element = ET.SubElement(title_detail, f'{ns}TitleElement')
    ET.SubElement(title_element, f'{ns}TitleElementLevel').text = '02'  # Collection level
    ET.SubElement(title_element, f'{ns}TitleText').text = series_name
    ET.SubElement(title_element, f'{ns}PartNumber').text = number

def _add_price(product_supply, ns: str, amount: str):
    """Add price information."""
    supply_detail = ET.SubElement(product_supply, f'{ns}SupplyDetail')
    supplier = ET.SubElement(supply_detail, f'{ns}Supplier')
    ET.SubElement(supplier, f'{ns}SupplierRole').text = '09'  # Publisher to end customers
    price = ET.SubElement(supply_detail, f'{ns}Price')
    ET.SubElement(price, f'{ns}PriceType').text = '02'  # RRP including tax
    ET.SubElement(price, f'{ns}PriceAmount').text = amount
    ET.SubElement(price, f'{ns}CurrencyCode').text = 'USD'

def _add_cover_image(descriptive_detail, ns: str, url: str):
    """Add cover image resource."""
    resource = ET.SubElement(descriptive_detail, f'{ns}SupportingResource')
    ET.SubElement(resource, f'{ns}ResourceContentType').text = '01'  # Front cover
    ET.SubElement(resource, f'{ns}ContentAudience').text = '00'  # Unrestricted
    resource_version = ET.SubElement(resource, f'{ns}ResourceVersion')
    ET.SubElement(resource_version, f'{ns}ResourceForm').text = '02'  # Digital download
    ET.SubElement(resource_version, f'{ns}ResourceVersionFeature')
    ET.SubElement(resource_version, f'{ns}ResourceLink').text = url

def main():
    """Generate complete test suite."""
    
    test_dir = Path('test_onix_files')
    test_dir.mkdir(exist_ok=True)
    
    print("🔄 Generating ONIX test files...")
    
    # Generate files with different completeness levels
    test_cases = [
        ('minimal', 'Should score very low, basic validation pass'),
        ('basic', 'Should score ~40-50%, meets minimum requirements'),
        ('good', 'Should score 75%+, Nielsen target level'),
        ('excellent', 'Should score 90%+, maximum completeness'),
        ('problematic', 'Should trigger validation errors and warnings')
    ]
    
    for level, description in test_cases:
        # Both namespaced and non-namespaced versions
        create_onix_file(level, f'{test_dir}/{level}_namespaced.xml', use_namespace=True)
        create_onix_file(level, f'{test_dir}/{level}_simple.xml', use_namespace=False)
    
    # Create batch test set
    batch_dir = test_dir / 'batch_test'
    batch_dir.mkdir(exist_ok=True)
    
    for i in range(5):
        level = random.choice(['basic', 'good', 'excellent'])
        create_onix_file(level, f'{batch_dir}/book_{i+1:02d}_{level}.xml', use_namespace=True)
    
    print(f"\n✅ Generated {len(list(test_dir.glob('**/*.xml')))} test files in {test_dir}/")
    print(f"📁 Batch testing files in {batch_dir}/")
    print(f"\n🧪 Test commands:")
    print(f"  Single file: python -m metaops.cli.main validate-full --onix {test_dir}/excellent_namespaced.xml")
    print(f"  Nielsen score: python -m metaops.cli.main nielsen-score --onix {test_dir}/good_namespaced.xml")
    print(f"  Retailer analysis: python -m metaops.cli.main multi-retailer --onix {test_dir}/basic_namespaced.xml")
    print(f"  Web interface: python -m metaops.cli.main web")
    print(f"  Batch dashboard: python -m metaops.cli.main dashboard")

if __name__ == '__main__':
    main()