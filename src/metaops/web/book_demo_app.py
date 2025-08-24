#!/usr/bin/env python3
"""
MetaOps Book-Author-Contract Management Demo
Main Streamlit application for publisher workflow management.
"""

import streamlit as st
import requests
import json
import pandas as pd
from datetime import date, datetime, timedelta
from typing import Dict, Any, List, Optional
import uuid

# Configure page
st.set_page_config(
    page_title="MetaOps Publisher Management",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API Configuration
API_BASE = "http://100.111.114.84:8002/api/v1"
AUTH_TOKEN = "demo.eyJ1c2VyX2lkIjoiZGVtb191c2VyIn0.signature"
HEADERS = {
    "Authorization": f"Bearer {AUTH_TOKEN}",
    "Content-Type": "application/json"
}

# Custom CSS for professional business tool aesthetic
def load_css():
    st.markdown("""
    <style>
        .main-header {
            background: linear-gradient(90deg, #1f2937 0%, #374151 100%);
            color: white;
            padding: 1rem 2rem;
            border-radius: 0.5rem;
            margin-bottom: 2rem;
        }
        .metric-card {
            background: #f8f9fa;
            padding: 1.5rem;
            border-radius: 0.5rem;
            border: 1px solid #e5e7eb;
            text-align: center;
            height: 100%;
        }
        .publisher-card {
            background: white;
            padding: 1.5rem;
            border-radius: 0.5rem;
            border: 1px solid #e5e7eb;
            margin-bottom: 1rem;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }
        .book-card {
            background: white;
            padding: 1rem;
            border-radius: 0.5rem;
            border-left: 4px solid #3b82f6;
            margin-bottom: 0.5rem;
            box-shadow: 0 1px 2px rgba(0,0,0,0.05);
        }
        .contract-compliant { border-left: 4px solid #10b981; }
        .contract-warning { border-left: 4px solid #f59e0b; }
        .contract-error { border-left: 4px solid #ef4444; }
        .status-badge {
            padding: 0.25rem 0.75rem;
            border-radius: 9999px;
            font-size: 0.75rem;
            font-weight: 600;
        }
        .status-compliant { 
            background: #d1fae5; 
            color: #065f46; 
        }
        .status-warning { 
            background: #fef3c7; 
            color: #92400e; 
        }
        .status-error { 
            background: #fee2e2; 
            color: #991b1b; 
        }
        .sidebar .sidebar-content {
            background: #f9fafb;
        }
        .action-button {
            background: #3b82f6;
            color: white;
            padding: 0.5rem 1rem;
            border-radius: 0.25rem;
            border: none;
            font-weight: 600;
            cursor: pointer;
        }
        .action-button:hover {
            background: #2563eb;
        }
        .data-table {
            border: 1px solid #e5e7eb;
            border-radius: 0.5rem;
            overflow: hidden;
        }
    </style>
    """, unsafe_allow_html=True)

# API helper functions
def make_api_request(method: str, endpoint: str, data: dict = None) -> Optional[Dict]:
    """Make API request with error handling"""
    url = f"{API_BASE}{endpoint}"
    
    try:
        if method == "GET":
            response = requests.get(url, headers=HEADERS)
        elif method == "POST":
            response = requests.post(url, headers=HEADERS, json=data)
        elif method == "PUT":
            response = requests.put(url, headers=HEADERS, json=data)
        else:
            return None
            
        if response.status_code in [200, 201]:
            return response.json()
        else:
            st.error(f"API Error: {response.status_code} - {response.text}")
            return None
    except requests.exceptions.ConnectionError:
        st.error("🚨 Cannot connect to API. Make sure the server is running on port 8002.")
        return None
    except Exception as e:
        st.error(f"Request failed: {e}")
        return None

def get_publishers() -> List[Dict]:
    """Get all publishers"""
    publishers = make_api_request("GET", "/publishers")
    return publishers if publishers else []

def get_publisher_dashboard(publisher_id: str) -> Optional[Dict]:
    """Get publisher dashboard data"""
    return make_api_request("GET", f"/publishers/{publisher_id}/dashboard")

def get_books(publisher_id: str = None) -> List[Dict]:
    """Get books, optionally filtered by publisher"""
    endpoint = "/books"
    if publisher_id:
        endpoint += f"?publisher_id={publisher_id}"
    books = make_api_request("GET", endpoint)
    return books if books else []

def get_book_details(book_id: str) -> Optional[Dict]:
    """Get detailed book information"""
    return make_api_request("GET", f"/books/{book_id}")

def search_authors(query: str) -> List[Dict]:
    """Search for authors"""
    authors = make_api_request("GET", f"/authors/search?q={query}")
    return authors if authors else []

def get_contracts(publisher_id: str) -> List[Dict]:
    """Get contracts for publisher"""
    contracts = make_api_request("GET", f"/contracts?publisher_id={publisher_id}")
    return contracts if contracts else []

def check_compliance(book_id: str, contract_id: str) -> Optional[Dict]:
    """Check book compliance against contract"""
    return make_api_request("POST", f"/books/{book_id}/check-compliance?contract_id={contract_id}")

def get_onix_preview(book_id: str) -> Optional[Dict]:
    """Get ONIX preview for a book"""
    return make_api_request("GET", f"/books/{book_id}/onix-preview")

def generate_onix(book_id: str, contract_id: Optional[str] = None, target_territory: Optional[str] = None) -> Optional[Dict]:
    """Generate full ONIX XML for a book"""
    params = []
    if contract_id:
        params.append(f"contract_id={contract_id}")
    if target_territory:
        params.append(f"target_territory={target_territory}")
    
    query_string = "&".join(params)
    endpoint = f"/books/{book_id}/onix"
    if query_string:
        endpoint += f"?{query_string}"
    
    return make_api_request("GET", endpoint)

# UI Components
def render_header():
    """Render main application header"""
    st.markdown("""
    <div class="main-header">
        <h1>📚 MetaOps Publisher Management</h1>
        <p>Complete book-author-contract workflow management</p>
    </div>
    """, unsafe_allow_html=True)

def render_publisher_selector():
    """Render publisher selection in sidebar"""
    st.sidebar.header("🏢 Publisher Selection")
    
    publishers = get_publishers()
    if not publishers:
        st.sidebar.error("No publishers found.")
        with st.sidebar.expander("🚀 Quick Setup", expanded=True):
            st.write("**Get started in 2 steps:**")
            st.write("1. Run sample data generator:")
            st.code("python generate_sample_data.py")
            st.write("2. Refresh this page")
            if st.button("🔄 Refresh Page"):
                st.rerun()
        return None
    
    # Create publisher options
    publisher_options = {f"{pub['name']} ({pub['imprint']})": pub for pub in publishers}
    
    selected_name = st.sidebar.selectbox(
        "Select Publisher",
        options=list(publisher_options.keys()),
        key="publisher_selector"
    )
    
    return publisher_options[selected_name] if selected_name else None

def render_navigation():
    """Render main navigation"""
    st.sidebar.header("📋 Navigation")
    
    nav_options = [
        "📊 Publisher Dashboard",
        "📚 Book Management", 
        "✍️ Author Search",
        "📄 Contract Management",
        "🔍 Compliance Checking"
    ]
    
    return st.sidebar.radio(
        "Choose View",
        nav_options,
        key="main_navigation"
    )

def render_publisher_dashboard(publisher: Dict):
    """Render publisher dashboard with metrics"""
    st.header(f"📊 {publisher['name']} Dashboard")
    
    # Get dashboard data
    dashboard = get_publisher_dashboard(publisher['id'])
    if not dashboard:
        st.error("Failed to load dashboard data")
        st.info("Make sure the API server is running and accessible.")
        return
    
    # Debug info (temporary)
    with st.expander("Debug Info (click to expand)", expanded=False):
        st.json(dashboard)
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <h3>{dashboard['metrics']['book_count']}</h3>
            <p>Total Books</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <h3>{dashboard['metrics']['contract_count']}</h3>
            <p>Active Contracts</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        compliance_rate = dashboard['compliance']['compliance_rate']
        st.markdown(f"""
        <div class="metric-card">
            <h3>{compliance_rate}%</h3>
            <p>Compliance Rate</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        total_checks = dashboard['compliance']['total_compliance_checks']
        st.markdown(f"""
        <div class="metric-card">
            <h3>{total_checks}</h3>
            <p>Compliance Checks</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Recent books
    st.subheader("📚 Recent Books")
    recent_books = dashboard['recent_books']
    
    if recent_books:
        for book in recent_books:
            status_class = "status-compliant" if book.get('validation_status') == 'approved' else "status-warning"
            st.markdown(f"""
            <div class="book-card">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <strong>{book['title']}</strong><br>
                        <small>ISBN: {book['isbn']}</small>
                    </div>
                    <span class="status-badge {status_class}">
                        {book.get('validation_status', 'pending').title()}
                    </span>
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No books found. Start by adding some books to your catalog.")

def render_book_management(publisher: Dict):
    """Render book management interface"""
    st.header("📚 Book Management")
    
    # Tabs for different book operations
    tab1, tab2, tab3, tab4 = st.tabs(["📖 Book Catalog", "➕ Add New Book", "🔗 Link Authors", "📄 ONIX Generation"])
    
    with tab1:
        st.subheader("Book Catalog")
        books = get_books(publisher['id'])
        
        if books:
            # Display books in cards
            for book in books:
                with st.expander(f"📖 {book['title']} (ISBN: {book['isbn']})"):
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        st.write(f"**Title:** {book['title']}")
                        st.write(f"**ISBN:** {book['isbn']}")
                        if book['subtitle']:
                            st.write(f"**Subtitle:** {book['subtitle']}")
                        st.write(f"**Publication Date:** {book.get('publication_date', 'Not set')}")
                        st.write(f"**Product Form:** {book['product_form']}")
                        st.write(f"**Status:** {book['validation_status'].title()}")
                    
                    with col2:
                        st.write("**Authors:**")
                        if book['authors']:
                            for author in book['authors']:
                                st.write(f"• {author['name']}")
                        else:
                            st.write("No authors linked")
                        
                        # Action buttons
                        btn_col1, btn_col2 = st.columns(2)
                        with btn_col1:
                            if st.button(f"📄 ONIX Preview", key=f"onix_{book['id']}"):
                                show_onix_preview(book['id'])
                        with btn_col2:
                            if st.button(f"View Details", key=f"details_{book['id']}"):
                                st.session_state.selected_book_id = book['id']
        else:
            st.info("📚 No books found for this publisher.")
            st.write("**Get started by:**")
            st.write("• Add a new book using the 'Add New Book' tab")
            st.write("• Run the sample data generator for demo data")
            st.write("• Switch to a different publisher")
    
    with tab2:
        st.subheader("Add New Book")
        render_add_book_form(publisher)
    
    with tab3:
        st.subheader("Link Authors to Books")
        render_author_linking_interface(publisher)
    
    with tab4:
        st.subheader("ONIX Generation")
        render_onix_generation_interface(publisher)

def render_add_book_form(publisher: Dict):
    """Render form to add new book"""
    with st.form("add_book_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            title = st.text_input("Book Title*", placeholder="Enter book title")
            isbn = st.text_input("ISBN*", placeholder="13-digit ISBN")
            subtitle = st.text_input("Subtitle", placeholder="Optional subtitle")
        
        with col2:
            pub_date = st.date_input("Publication Date", value=date.today())
            product_form = st.selectbox("Product Form", ["BB", "BC", "BA", "DG", "DA"])
        
        submitted = st.form_submit_button("Add Book")
        
        if submitted:
            if not title or not isbn:
                st.error("Title and ISBN are required fields.")
                return
            
            if len(isbn) != 13 or not isbn.isdigit():
                st.error("ISBN must be exactly 13 digits.")
                return
            
            book_data = {
                "title": title,
                "isbn": isbn,
                "subtitle": subtitle if subtitle else None,
                "publisher_id": publisher['id'],
                "publication_date": pub_date.isoformat(),
                "product_form": product_form
            }
            
            result = make_api_request("POST", "/books", book_data)
            if result:
                st.success(f"✅ Book '{title}' created successfully!")
                st.rerun()
            else:
                st.error("Failed to create book. Check ISBN uniqueness.")

def render_author_linking_interface(publisher: Dict):
    """Render interface for linking authors to books"""
    books = get_books(publisher['id'])
    
    if not books:
        st.info("No books available for author linking.")
        return
    
    # Select book
    book_options = {f"{book['title']} (ISBN: {book['isbn']})": book for book in books}
    selected_book_name = st.selectbox("Select Book", list(book_options.keys()))
    selected_book = book_options[selected_book_name]
    
    # Search authors
    st.subheader("Search Authors")
    search_term = st.text_input("Author Name", placeholder="Search for authors...")
    
    if search_term:
        authors = search_authors(search_term)
        if authors:
            st.write("**Search Results:**")
            for author in authors:
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(f"**{author['name']}** ({author['contributor_type']})")
                    st.write(f"Books: {author['book_count']} • Bio: {author['biography'][:100]}...")
                
                with col2:
                    if st.button("Link Author", key=f"link_{author['id']}"):
                        # Link author to book
                        link_data = [{
                            "author_id": author['id'],
                            "sequence_number": 1,
                            "contributor_role": "A01"
                        }]
                        
                        result = make_api_request("PUT", f"/books/{selected_book['id']}/authors", link_data)
                        if result:
                            st.success(f"✅ Linked {author['name']} to {selected_book['title']}")
                            st.rerun()
                        else:
                            st.error("Failed to link author")

def render_onix_generation_interface(publisher: Dict):
    """Render ONIX generation interface"""
    books = get_books(publisher['id'])
    contracts = get_contracts(publisher['id'])
    
    if not books:
        st.info("No books available for ONIX generation.")
        return
    
    # Select book
    book_options = {f"{book['title']} (ISBN: {book['isbn']})": book for book in books}
    selected_book_name = st.selectbox("Select Book for ONIX Generation", list(book_options.keys()), key="onix_book_select")
    selected_book = book_options[selected_book_name]
    
    # Show book details
    col1, col2 = st.columns(2)
    with col1:
        st.write(f"**Title:** {selected_book['title']}")
        st.write(f"**ISBN:** {selected_book['isbn']}")
        st.write(f"**Authors:** {len(selected_book['authors'])} linked")
    with col2:
        st.write(f"**Product Form:** {selected_book['product_form']}")
        st.write(f"**Publication Date:** {selected_book.get('publication_date', 'Not set')}")
        st.write(f"**Status:** {selected_book['validation_status'].title()}")
    
    st.divider()
    
    # Advanced options
    with st.expander("🎛️ Advanced ONIX Options"):
        # Contract-based filtering
        contract_filter = st.checkbox("Apply Contract Filtering", help="Filter ONIX output based on contract terms")
        selected_contract = None
        if contract_filter and contracts:
            contract_options = {f"{contract['contract_name']} ({contract['retailer']})": contract for contract in contracts}
            if contract_options:
                selected_contract_name = st.selectbox("Select Contract", list(contract_options.keys()))
                selected_contract = contract_options[selected_contract_name]
        
        # Territory targeting
        territory_filter = st.checkbox("Target Specific Territory", help="Generate ONIX for specific territory")
        target_territory = None
        if territory_filter:
            target_territory = st.selectbox("Target Territory", ["US", "UK", "CA", "AU", "EU"], help="Territory for ONIX optimization")
    
    st.divider()
    
    # Generation actions
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("👁️ Quick Preview", use_container_width=True):
            with st.spinner("Generating preview..."):
                preview_data = get_onix_preview(selected_book['id'])
                
                if preview_data:
                    st.success("✅ Preview generated!")
                    st.subheader("ONIX Preview")
                    st.code(preview_data.get('preview_xml', 'No preview available'), language='xml')
                else:
                    st.error("Failed to generate preview")
    
    with col2:
        if st.button("📄 Generate Full ONIX", use_container_width=True):
            with st.spinner("Generating full ONIX..."):
                full_onix = generate_onix(
                    selected_book['id'],
                    contract_id=selected_contract['id'] if selected_contract else None,
                    target_territory=target_territory
                )
                
                if full_onix:
                    st.success("✅ Full ONIX generated!")
                    
                    # Show generation info
                    st.write(f"**Generated:** {full_onix.get('generated_at', 'Now')}")
                    if selected_contract:
                        st.write(f"**Applied Contract:** {selected_contract['contract_name']}")
                    if target_territory:
                        st.write(f"**Territory:** {target_territory}")
                    
                    # Download button
                    xml_content = full_onix.get('onix_xml', '')
                    if xml_content:
                        st.download_button(
                            label="📥 Download ONIX XML",
                            data=xml_content,
                            file_name=f"{selected_book['isbn']}_onix.xml",
                            mime="application/xml"
                        )
                else:
                    st.error("Failed to generate ONIX")
    
    with col3:
        if st.button("🔍 Validate Generated ONIX", use_container_width=True):
            st.info("ONIX validation integration coming soon!")

def render_author_search():
    """Render author search interface"""
    st.header("✍️ Author Search & Management")
    
    # Search interface
    col1, col2 = st.columns([3, 1])
    with col1:
        search_query = st.text_input("Search Authors", placeholder="Enter author name...")
    with col2:
        search_button = st.button("🔍 Search")
    
    if search_query or search_button:
        authors = search_authors(search_query if search_query else "")
        
        if authors:
            st.subheader(f"Found {len(authors)} authors")
            
            for author in authors:
                with st.expander(f"✍️ {author['name']}"):
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        st.write(f"**Name:** {author['name']}")
                        st.write(f"**Sort Name:** {author['sort_name']}")
                        st.write(f"**Contributor Type:** {author['contributor_type']}")
                        st.write(f"**Biography:** {author.get('biography', 'No biography available')}")
                        if author.get('website_url'):
                            st.write(f"**Website:** {author['website_url']}")
                    
                    with col2:
                        st.metric("Books Written", author['book_count'])
                        st.write(f"**ID:** {author['id'][:8]}...")
        else:
            st.info("No authors found. Try a different search term.")

def render_compliance_checking(publisher: Dict):
    """Render compliance checking interface"""
    st.header("🔍 Contract Compliance Checking")
    
    # Get books and contracts
    books = get_books(publisher['id'])
    contracts = get_contracts(publisher['id'])
    
    if not books:
        st.info("No books available for compliance checking.")
        return
    
    if not contracts:
        st.info("No contracts available. Create contracts first.")
        return
    
    # Select book and contract
    col1, col2 = st.columns(2)
    
    with col1:
        book_options = {f"{book['title']} (ISBN: {book['isbn']})": book for book in books}
        selected_book_name = st.selectbox("Select Book", list(book_options.keys()))
        selected_book = book_options[selected_book_name]
    
    with col2:
        contract_options = {f"{contract['contract_name']} ({contract['retailer']})": contract for contract in contracts}
        selected_contract_name = st.selectbox("Select Contract", list(contract_options.keys()))
        selected_contract = contract_options[selected_contract_name]
    
    if st.button("🔍 Check Compliance"):
        compliance = check_compliance(selected_book['id'], selected_contract['id'])
        
        if compliance:
            # Display results
            st.subheader("Compliance Results")
            
            # Status badge
            status = compliance['status']
            if status == 'compliant':
                st.success(f"✅ **{status.title()}** - Book meets all contract requirements")
            elif status == 'review_needed':
                st.warning(f"⚠️ **Needs Review** - Some issues require attention")
            else:
                st.error(f"❌ **Non-Compliant** - Critical issues found")
            
            # Detailed results
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Territory Check")
                if compliance['territory_check_passed']:
                    st.success("✅ Territory restrictions satisfied")
                else:
                    st.error("❌ Territory restrictions failed")
            
            with col2:
                st.subheader("Rules Check")
                if compliance['rules_check_passed']:
                    st.success("✅ Contract rules satisfied")
                else:
                    st.error("❌ Contract rules failed")
            
            # Violations and warnings
            if compliance['violations']:
                st.subheader("❌ Violations")
                for violation in compliance['violations']:
                    st.error(f"• {violation}")
            
            if compliance['warnings']:
                st.subheader("⚠️ Warnings")
                for warning in compliance['warnings']:
                    st.warning(f"• {warning}")
            
            if not compliance['violations'] and not compliance['warnings']:
                st.info("No specific issues to report.")

def show_onix_preview(book_id: str):
    """Show ONIX preview in a modal-like dialog"""
    preview_data = get_onix_preview(book_id)
    
    if preview_data:
        st.subheader("📄 ONIX Preview")
        st.info("This is a truncated preview of the generated ONIX XML.")
        
        # Show the XML in a code block
        st.code(preview_data.get('preview_xml', 'No preview available'), language='xml')
        
        # Option to generate full ONIX
        if st.button("Generate Full ONIX", key=f"full_onix_{book_id}"):
            with st.spinner("Generating full ONIX..."):
                full_onix = generate_onix(book_id)
                
                if full_onix:
                    st.success("✅ Full ONIX generated successfully!")
                    
                    # Download button for full XML
                    xml_content = full_onix.get('onix_xml', '')
                    if xml_content:
                        st.download_button(
                            label="📥 Download ONIX XML",
                            data=xml_content,
                            file_name=f"book_{book_id}_onix.xml",
                            mime="application/xml",
                            key=f"download_onix_{book_id}"
                        )
                        
                        # Show generation metadata
                        st.write(f"**Generated:** {full_onix.get('generated_at', 'Unknown')}")
                        if full_onix.get('contract_id'):
                            st.write(f"**Contract:** {full_onix.get('contract_id')}")
                        if full_onix.get('target_territory'):
                            st.write(f"**Territory:** {full_onix.get('target_territory')}")
    else:
        st.error("Failed to generate ONIX preview. Please ensure the book has all required metadata.")

def render_contract_management(publisher: Dict):
    """Render comprehensive contract management interface"""
    st.header("📄 Contract Management & Distribution Workflow")
    
    # Tabs for contract operations
    tab1, tab2, tab3, tab4 = st.tabs(["📋 Active Contracts", "➕ Create Contract", "🌐 Distributor Integration", "📈 Business Workflow"])
    
    with tab1:
        st.subheader("Active Contracts")
        contracts = get_contracts(publisher['id'])
        
        if contracts:
            # Contract metrics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Contracts", len(contracts))
            with col2:
                active_count = len([c for c in contracts if c.get('status') == 'active'])
                st.metric("Active", active_count)
            with col3:
                pending_count = len([c for c in contracts if c.get('status') == 'pending'])
                st.metric("Pending", pending_count)
            with col4:
                territories = set()
                for contract in contracts:
                    if contract.get('territory_restrictions'):
                        territories.update(contract['territory_restrictions'])
                st.metric("Territories", len(territories))
            
            st.divider()
            
            # Contract list
            for contract in contracts:
                with st.expander(f"📄 {contract['contract_name']} ({contract['retailer']})", expanded=False):
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        st.write(f"**Retailer:** {contract['retailer']}")
                        st.write(f"**Type:** {contract['contract_type'].replace('_', ' ').title()}")
                        st.write(f"**Status:** {contract['status'].title()}")
                        if contract.get('effective_date'):
                            st.write(f"**Effective Date:** {contract['effective_date']}")
                        if contract.get('territory_restrictions'):
                            st.write(f"**Territories:** {', '.join(contract['territory_restrictions'])}")
                    
                    with col2:
                        st.write("**Actions:**")
                        if st.button(f"📊 View Analytics", key=f"analytics_{contract['id']}"):
                            show_contract_analytics(contract['id'])
                        if st.button(f"📤 Send ONIX Feed", key=f"feed_{contract['id']}"):
                            simulate_distributor_feed(contract, publisher)
                        if st.button(f"🔍 Test Compliance", key=f"test_{contract['id']}"):
                            test_contract_compliance(contract['id'], publisher['id'])
        else:
            st.info("📄 No contracts found for this publisher.")
            st.write("**Get started by:**")
            st.write("• Create your first contract using the 'Create Contract' tab")
            st.write("• Set up distribution agreements with major retailers")
            st.write("• Configure territory restrictions and validation rules")
    
    with tab2:
        st.subheader("Create New Contract")
        render_create_contract_form(publisher)
    
    with tab3:
        st.subheader("Distributor Integration")
        render_distributor_integration(publisher)
    
    with tab4:
        st.subheader("Business Workflow Visualization")
        render_business_workflow(publisher)

def show_contract_analytics(contract_id: str):
    """Show contract performance analytics"""
    st.subheader("📊 Contract Analytics")
    
    # Placeholder analytics - in a real system, this would pull actual data
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Books Distributed", "147", delta="12")
    with col2:
        st.metric("Compliance Rate", "94%", delta="2%")
    with col3:
        st.metric("Revenue Impact", "$23,450", delta="$1,230")
    
    st.info("📈 Detailed analytics integration coming soon.")

def simulate_distributor_feed(contract: Dict, publisher: Dict):
    """Simulate sending ONIX feed to distributor"""
    st.subheader(f"📤 Simulating Feed to {contract['retailer'].title()}")
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    import time
    
    # Simulate feed generation process
    steps = [
        ("Gathering book metadata...", 20),
        ("Applying contract filters...", 40),
        ("Generating ONIX XML...", 60),
        ("Validating feed...", 80),
        ("Transmitting to distributor...", 100)
    ]
    
    for step, progress in steps:
        status_text.text(step)
        progress_bar.progress(progress)
        time.sleep(0.5)
    
    st.success(f"✅ Feed successfully sent to {contract['retailer'].title()}!")
    st.json({
        "feed_id": "FD-2025-001234",
        "books_included": 23,
        "territory": contract.get('territory_restrictions', ['US'])[0],
        "format": "ONIX 3.0",
        "timestamp": "2025-08-24T05:30:00Z"
    })

def test_contract_compliance(contract_id: str, publisher_id: str):
    """Test contract compliance across all books"""
    st.subheader("🔍 Contract Compliance Testing")
    
    books = get_books(publisher_id)
    if not books:
        st.warning("No books available for compliance testing.")
        return
    
    # Simulate compliance testing
    compliance_results = []
    for book in books[:5]:  # Test first 5 books
        # This would call the actual API in a real implementation
        result = {
            "book": book['title'],
            "isbn": book['isbn'],
            "compliant": True,  # Simulated
            "issues": []
        }
        compliance_results.append(result)
    
    # Display results
    compliant_count = sum(1 for r in compliance_results if r['compliant'])
    st.metric("Books Tested", len(compliance_results))
    st.metric("Compliant", compliant_count)
    st.metric("Issues Found", len(compliance_results) - compliant_count)
    
    for result in compliance_results:
        status_color = "🟢" if result['compliant'] else "🔴"
        st.write(f"{status_color} **{result['book']}** ({result['isbn']})")

def render_create_contract_form(publisher: Dict):
    """Render form to create new contracts"""
    with st.form("create_contract_form"):
        st.write("**Contract Details**")
        
        col1, col2 = st.columns(2)
        with col1:
            contract_name = st.text_input("Contract Name*", placeholder="e.g., Amazon KDP Agreement 2025")
            contract_type = st.selectbox("Contract Type*", 
                ["distribution_agreement", "retailer_terms", "licensing"])
            retailer = st.text_input("Retailer/Partner*", placeholder="e.g., Amazon, B&N, Apple")
        
        with col2:
            effective_date = st.date_input("Effective Date")
            expiration_date = st.date_input("Expiration Date")
            territory_restrictions = st.multiselect(
                "Territory Restrictions",
                ["US", "UK", "CA", "AU", "EU", "DE", "FR", "JP", "IN"],
                default=["US"]
            )
        
        st.write("**Validation Rules**")
        required_fields = st.multiselect(
            "Required ONIX Fields",
            ["isbn", "title", "author", "publication_date", "price", "description"],
            default=["isbn", "title"]
        )
        
        min_discount = st.slider("Minimum Discount %", 0, 50, 25)
        max_discount = st.slider("Maximum Discount %", 25, 75, 50)
        
        submitted = st.form_submit_button("Create Contract")
        
        if submitted:
            if not contract_name or not retailer:
                st.error("Contract name and retailer are required fields.")
                return
            
            validation_rules = {
                "required_fields": required_fields,
                "min_discount": min_discount / 100,
                "max_discount": max_discount / 100
            }
            
            contract_data = {
                "publisher_id": publisher['id'],
                "contract_name": contract_name,
                "contract_type": contract_type,
                "retailer": retailer,
                "effective_date": effective_date.isoformat(),
                "expiration_date": expiration_date.isoformat(),
                "territory_restrictions": territory_restrictions,
                "validation_rules": validation_rules
            }
            
            result = make_api_request("POST", "/contracts", contract_data)
            if result:
                st.success(f"✅ Contract '{contract_name}' created successfully!")
                st.rerun()
            else:
                st.error("Failed to create contract.")

def render_distributor_integration(publisher: Dict):
    """Render distributor integration simulation"""
    st.write("**Major Distributors & Retailers**")
    
    distributors = [
        {"name": "Amazon KDP", "status": "connected", "last_sync": "2 hours ago", "books": 156},
        {"name": "Ingram Content", "status": "connected", "last_sync": "1 day ago", "books": 142},
        {"name": "Barnes & Noble", "status": "pending", "last_sync": "Never", "books": 0},
        {"name": "Apple Books", "status": "connected", "last_sync": "6 hours ago", "books": 89},
        {"name": "Kobo", "status": "disconnected", "last_sync": "1 week ago", "books": 45},
    ]
    
    for dist in distributors:
        with st.container():
            col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
            
            with col1:
                status_icon = {"connected": "🟢", "pending": "🟡", "disconnected": "🔴"}[dist["status"]]
                st.write(f"{status_icon} **{dist['name']}**")
            
            with col2:
                st.write(f"Status: {dist['status'].title()}")
            
            with col3:
                st.write(f"Books: {dist['books']}")
            
            with col4:
                if dist["status"] == "connected":
                    if st.button("🔄 Sync", key=f"sync_{dist['name']}"):
                        st.success(f"Syncing with {dist['name']}...")
                else:
                    if st.button("🔗 Connect", key=f"connect_{dist['name']}"):
                        st.info(f"Connecting to {dist['name']}...")
        
        st.divider()

def render_business_workflow(publisher: Dict):
    """Render business workflow visualization"""
    st.write("**Publishing Workflow Overview**")
    
    # Workflow steps
    workflow_steps = [
        {"step": "1. Create Book", "status": "complete", "description": "Add book metadata and authors"},
        {"step": "2. Generate ONIX", "status": "complete", "description": "Create distributor-ready XML feeds"},
        {"step": "3. Contract Review", "status": "in_progress", "description": "Verify compliance with retailer terms"},
        {"step": "4. Distribute", "status": "pending", "description": "Send feeds to retailers and distributors"},
        {"step": "5. Monitor", "status": "pending", "description": "Track sales and compliance metrics"}
    ]
    
    for i, step in enumerate(workflow_steps):
        col1, col2 = st.columns([1, 3])
        
        with col1:
            if step["status"] == "complete":
                st.success(f"✅ {step['step']}")
            elif step["status"] == "in_progress":
                st.warning(f"🔄 {step['step']}")
            else:
                st.info(f"⏳ {step['step']}")
        
        with col2:
            st.write(step["description"])
        
        if i < len(workflow_steps) - 1:
            st.write("↓")
    
    st.divider()
    
    # Business metrics
    st.subheader("📊 Business Impact")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Books Published", "47", delta="3")
    with col2:
        st.metric("Active Contracts", "8", delta="1")
    with col3:
        st.metric("Territories", "12", delta="2")
    with col4:
        st.metric("Compliance Rate", "96%", delta="1%")

def main():
    """Main application entry point"""
    load_css()
    render_header()
    
    # Check API health
    health = make_api_request("GET", "/health")
    if not health:
        st.error("🚨 Cannot connect to MetaOps API. Please start the server first:")
        st.code("python -m uvicorn metaops.api.main:app --port 8002 --host 0.0.0.0")
        st.stop()
    
    # Publisher selection
    publisher = render_publisher_selector()
    if not publisher:
        st.info("Please select a publisher to continue.")
        st.stop()
    
    # Navigation
    selected_view = render_navigation()
    
    # Render selected view
    if selected_view == "📊 Publisher Dashboard":
        render_publisher_dashboard(publisher)
    elif selected_view == "📚 Book Management":
        render_book_management(publisher)
    elif selected_view == "✍️ Author Search":
        render_author_search()
    elif selected_view == "📄 Contract Management":
        render_contract_management(publisher)
    elif selected_view == "🔍 Compliance Checking":
        render_compliance_checking(publisher)

if __name__ == "__main__":
    main()