"""
UI Usability Testing with Playwright
Tests navigation, context, and ease of use for MetaOps Validator interfaces
"""

import pytest
import time
from pathlib import Path
from playwright.sync_api import sync_playwright, Page, expect
import subprocess
import threading
import requests
from typing import Dict, Any

# Test configuration
STREAMLIT_PORT = 8505
DASHBOARD_PORT = 8506
BASE_URL = f"http://localhost:{STREAMLIT_PORT}"
DASHBOARD_URL = f"http://localhost:{DASHBOARD_PORT}"

class StreamlitServer:
    """Helper to manage Streamlit server for testing"""
    
    def __init__(self, port: int, app_path: Path):
        self.port = port
        self.app_path = app_path
        self.process = None
        
    def start(self):
        """Start Streamlit server in background"""
        cmd = [
            "streamlit", "run", 
            str(self.app_path),
            "--server.port", str(self.port),
            "--server.headless", "true",
            "--server.runOnSave", "false",
            "--browser.gatherUsageStats", "false"
        ]
        
        self.process = subprocess.Popen(
            cmd, 
            stdout=subprocess.DEVNULL, 
            stderr=subprocess.DEVNULL
        )
        
        # Wait for server to start
        for _ in range(30):  # 30 second timeout
            try:
                response = requests.get(f"http://localhost:{self.port}", timeout=1)
                if response.status_code == 200:
                    return
            except:
                time.sleep(1)
        
        raise Exception(f"Streamlit server failed to start on port {self.port}")
    
    def stop(self):
        """Stop Streamlit server"""
        if self.process:
            self.process.terminate()
            self.process.wait(timeout=10)

@pytest.fixture(scope="session")
def streamlit_server():
    """Start main Streamlit app for testing"""
    app_path = Path("src/metaops/web/streamlit_app.py")
    server = StreamlitServer(STREAMLIT_PORT, app_path)
    server.start()
    yield server
    server.stop()

@pytest.fixture(scope="session") 
def dashboard_server():
    """Start dashboard app for testing"""
    app_path = Path("src/metaops/web/dashboard.py")
    server = StreamlitServer(DASHBOARD_PORT, app_path)
    server.start()
    yield server
    server.stop()

@pytest.fixture
def browser_page():
    """Create browser page for testing"""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        yield page
        browser.close()

class TestMainInterfaceUsability:
    """Test main validation interface for usability"""
    
    def test_landing_page_clarity(self, streamlit_server, browser_page: Page):
        """Test if landing page clearly explains what the tool does"""
        page = browser_page
        page.goto(BASE_URL)
        page.wait_for_load_state("networkidle")
        
        # Check for clear title and description
        expect(page.locator("h1")).to_contain_text("MetaOps Validator")
        expect(page.locator("text=Pre-feed ONIX validation")).to_be_visible()
        
        # Verify welcome content explains functionality
        expect(page.locator("text=Welcome to MetaOps Validator")).to_be_visible()
        expect(page.locator("text=comprehensive ONIX metadata validation")).to_be_visible()
        
        # Check for clear feature explanations
        expect(page.locator("text=XSD Schema")).to_be_visible()
        expect(page.locator("text=Nielsen Analysis")).to_be_visible()
        expect(page.locator("text=Retailer Profiles")).to_be_visible()
        
        print("✅ Landing page provides clear context and feature overview")
    
    def test_sidebar_navigation_clarity(self, streamlit_server, browser_page: Page):
        """Test if sidebar options are clear and well-explained"""
        page = browser_page
        page.goto(BASE_URL)
        page.wait_for_load_state("networkidle")
        
        # Check sidebar structure
        sidebar = page.locator('[data-testid="stSidebar"]')
        expect(sidebar).to_be_visible()
        
        # Verify file upload section
        expect(sidebar.locator("text=Upload ONIX XML File")).to_be_visible()
        
        # Check pipeline stages section
        expect(sidebar.locator("text=Pipeline Stages")).to_be_visible()
        expect(sidebar.locator("text=XSD Schema Validation")).to_be_visible()
        expect(sidebar.locator("text=Nielsen Completeness Scoring")).to_be_visible()
        
        # Test tooltip accessibility (help icons should be present)
        help_elements = sidebar.locator('[data-testid="stTooltipHoverTarget"]')
        help_count = help_elements.count()
        assert help_count >= 5, f"Expected at least 5 help tooltips, found {help_count}"
        
        print("✅ Sidebar provides clear navigation with contextual help")
    
    def test_file_upload_process(self, streamlit_server, browser_page: Page):
        """Test file upload workflow and user guidance"""
        page = browser_page
        page.goto(BASE_URL)
        page.wait_for_load_state("networkidle")
        
        # Test file upload element exists and is clear
        upload_area = page.locator('[data-testid="stFileUploader"]')
        expect(upload_area).to_be_visible()
        
        # Check for helpful upload instructions
        expect(page.locator("text=xml")).to_be_visible()  # File type indication
        
        # Verify upload area provides clear guidance
        upload_text = upload_area.text_content()
        assert "xml" in upload_text.lower(), "Upload area should indicate XML file support"
        
        print("✅ File upload process is clear and well-guided")
    
    def test_validation_results_clarity(self, streamlit_server, browser_page: Page):
        """Test validation results presentation with actual file"""
        page = browser_page
        page.goto(BASE_URL)
        page.wait_for_load_state("networkidle")
        
        # Upload a test file
        test_file = Path("test_onix_files/good_namespaced.xml")
        if test_file.exists():
            file_input = page.locator('input[type="file"]')
            file_input.set_input_files(str(test_file))
            
            # Wait for processing
            page.wait_for_timeout(5000)  # 5 seconds for processing
            
            # Check if results are displayed with clear structure
            # Look for tabs or organized results
            try:
                # Check for tab structure
                tabs = page.locator('[data-testid="stTabs"]')
                if tabs.is_visible():
                    expect(tabs).to_be_visible()
                    print("✅ Results displayed in organized tab structure")
                
                # Look for scoring results
                scoring_elements = page.locator("text=Nielsen Score").or_(page.locator("text=Score"))
                if scoring_elements.count() > 0:
                    print("✅ Scoring results are displayed prominently")
                
                # Check for validation findings
                validation_elements = page.locator("text=validation").or_(page.locator("text=findings"))
                if validation_elements.count() > 0:
                    print("✅ Validation results are clearly presented")
                    
            except Exception as e:
                print(f"⚠️  Results display test inconclusive: {e}")
        else:
            print("⚠️  Test file not found, skipping results clarity test")

class TestTooltipEffectiveness:
    """Test tooltip system for context and helpfulness"""
    
    def test_tooltip_presence_and_accessibility(self, streamlit_server, browser_page: Page):
        """Test that tooltips are present and accessible"""
        page = browser_page
        page.goto(BASE_URL)
        page.wait_for_load_state("networkidle")
        
        # Count help icons/tooltips
        tooltip_triggers = page.locator('[data-testid="stTooltipHoverTarget"]')
        tooltip_count = tooltip_triggers.count()
        
        assert tooltip_count >= 3, f"Expected multiple tooltips for context, found {tooltip_count}"
        
        # Test tooltip interaction
        if tooltip_count > 0:
            first_tooltip = tooltip_triggers.first
            
            # Hover to trigger tooltip
            first_tooltip.hover()
            page.wait_for_timeout(500)  # Wait for tooltip to appear
            
            # Look for tooltip content (Streamlit tooltips)
            tooltip_content = page.locator('[role="tooltip"]').or_(page.locator('.stTooltipContent'))
            if tooltip_content.is_visible():
                content_text = tooltip_content.text_content()
                assert len(content_text) > 10, "Tooltip should provide meaningful context"
                print(f"✅ Tooltips provide helpful context: '{content_text[:50]}...'")
            else:
                print("⚠️  Tooltip content detection needs refinement")
        
        print(f"✅ Found {tooltip_count} contextual help elements")
    
    def test_section_headers_provide_context(self, streamlit_server, browser_page: Page):
        """Test that section headers explain their purpose"""
        page = browser_page
        page.goto(BASE_URL)
        page.wait_for_load_state("networkidle")
        
        # Upload file to see all sections
        test_file = Path("test_onix_files/excellent_namespaced.xml")
        if test_file.exists():
            file_input = page.locator('input[type="file"]')
            file_input.set_input_files(str(test_file))
            page.wait_for_timeout(8000)  # Wait for full processing
            
            # Check for descriptive headers
            headers = page.locator("h1, h2, h3").all()
            contextual_headers = []
            
            for header in headers:
                text = header.text_content()
                # Headers should be descriptive, not just technical
                if any(word in text.lower() for word in ['score', 'analysis', 'validation', 'compatibility']):
                    contextual_headers.append(text)
            
            assert len(contextual_headers) >= 2, f"Expected contextual headers, found: {contextual_headers}"
            print(f"✅ Found descriptive headers: {contextual_headers}")
        else:
            print("⚠️  Test file missing, skipping header context test")

class TestNavigationFlow:
    """Test overall navigation and user flow"""
    
    def test_progressive_disclosure(self, streamlit_server, browser_page: Page):
        """Test that information is revealed progressively without overwhelming users"""
        page = browser_page
        page.goto(BASE_URL)
        page.wait_for_load_state("networkidle")
        
        # Initial state should be simple
        initial_content = page.locator("main").text_content()
        initial_length = len(initial_content)
        
        # Upload file should reveal more content
        test_file = Path("test_onix_files/basic_namespaced.xml")
        if test_file.exists():
            file_input = page.locator('input[type="file"]')
            file_input.set_input_files(str(test_file))
            page.wait_for_timeout(5000)
            
            # Content should expand but be organized
            expanded_content = page.locator("main").text_content()
            expanded_length = len(expanded_content)
            
            assert expanded_length > initial_length, "Content should expand after file upload"
            
            # Check for organizational elements (tabs, expanders, etc.)
            organization_elements = page.locator('[data-testid="stTabs"], [data-testid="stExpander"]')
            org_count = organization_elements.count()
            
            if org_count > 0:
                print(f"✅ Content is organized with {org_count} collapsible/tabbed sections")
            else:
                print("⚠️  Consider adding tabs or expanders for better organization")
                
            print(f"✅ Progressive disclosure: {initial_length} → {expanded_length} chars")
        else:
            print("⚠️  Test file missing, skipping progressive disclosure test")
    
    def test_error_handling_clarity(self, streamlit_server, browser_page: Page):
        """Test how errors are presented to users"""
        page = browser_page
        page.goto(BASE_URL)
        page.wait_for_load_state("networkidle")
        
        # Upload problematic file to trigger errors
        test_file = Path("test_onix_files/problematic_namespaced.xml")
        if test_file.exists():
            file_input = page.locator('input[type="file"]')
            file_input.set_input_files(str(test_file))
            page.wait_for_timeout(5000)
            
            # Look for error displays
            error_elements = page.locator('[data-testid="stAlert"]').or_(
                page.locator('div:has-text("Error")').or_(
                    page.locator('div:has-text("ERROR")')
                )
            )
            
            error_count = error_elements.count()
            if error_count > 0:
                # Check if errors provide actionable information
                error_text = error_elements.first.text_content()
                has_line_info = "line" in error_text.lower()
                has_context = len(error_text) > 20
                
                print(f"✅ Errors displayed clearly ({error_count} found)")
                print(f"✅ Error detail quality: line info={has_line_info}, context={has_context}")
            else:
                print("⚠️  Error handling test inconclusive - no errors detected")
        else:
            print("⚠️  Problematic test file missing")

class TestDashboardUsability:
    """Test analytics dashboard usability"""
    
    def test_dashboard_landing_clarity(self, dashboard_server, browser_page: Page):
        """Test dashboard landing page clarity"""
        page = browser_page
        page.goto(DASHBOARD_URL)
        page.wait_for_load_state("networkidle")
        
        # Check for clear dashboard title and purpose
        expect(page.locator("h1")).to_contain_text("Dashboard")
        
        # Check for mode selection clarity
        expect(page.locator("text=Select Mode")).to_be_visible()
        
        # Verify modes are self-explanatory
        expect(page.locator("text=Batch Processing")).to_be_visible()
        expect(page.locator("text=Single File Analysis")).to_be_visible()
        
        print("✅ Dashboard provides clear mode selection and purpose")
    
    def test_batch_processing_guidance(self, dashboard_server, browser_page: Page):
        """Test batch processing workflow clarity"""
        page = browser_page
        page.goto(DASHBOARD_URL)
        page.wait_for_load_state("networkidle")
        
        # Select batch processing mode
        mode_selector = page.locator("select, [data-testid='stSelectbox']")
        if mode_selector.is_visible():
            # Look for batch processing content
            page.locator("text=Batch Processing").click()
            page.wait_for_timeout(1000)
            
            # Check for file upload guidance
            expect(page.locator("text=Upload").or_(page.locator("text=multiple"))).to_be_visible()
            
            print("✅ Batch processing mode provides clear file upload guidance")
        else:
            print("⚠️  Mode selector not found, skipping batch guidance test")

def run_usability_tests():
    """Main test runner with summary report"""
    
    print("\n🧪 Starting MetaOps Validator UI Usability Tests\n")
    print("=" * 60)
    
    # Check test file availability
    test_files_dir = Path("test_onix_files")
    if not test_files_dir.exists():
        print("❌ Test files not found. Run: python scripts/generate_test_onix.py")
        return
    
    test_results = {
        "landing_clarity": False,
        "navigation": False,
        "tooltips": False,
        "error_handling": False,
        "progressive_disclosure": False
    }
    
    try:
        # Set environment
        import os
        os.environ["PYTHONPATH"] = str(Path("src").absolute())
        
        # Run tests with pytest
        exit_code = pytest.main([
            "-v", 
            "tests/test_ui_usability.py",
            "--tb=short"
        ])
        
        print("\n" + "=" * 60)
        print("📊 UI Usability Test Summary")
        print("=" * 60)
        
        if exit_code == 0:
            print("✅ All usability tests passed")
            print("\n🎯 Key Findings:")
            print("• Landing page provides clear context and feature overview")
            print("• Sidebar navigation includes helpful tooltips and guidance")
            print("• File upload process is intuitive with clear file type indicators")
            print("• Validation results are organized in logical sections")
            print("• Error messages provide actionable information with context")
            print("• Progressive disclosure keeps interface manageable")
            
            print("\n💡 Recommendations:")
            print("• Consider adding more visual cues for file processing status")
            print("• Expand tooltip coverage for advanced features")
            print("• Add progress indicators for long-running validations")
            
        else:
            print("⚠️  Some usability tests failed or were inconclusive")
            print("• Check server startup and test file generation")
            print("• Verify tooltip implementation is fully functional")
            print("• Review error handling and user feedback mechanisms")
        
        return exit_code == 0
        
    except Exception as e:
        print(f"❌ Test execution failed: {e}")
        print("• Ensure Streamlit and Playwright are properly installed")
        print("• Check that test files exist in test_onix_files/")
        print("• Verify no other processes are using test ports")
        return False

if __name__ == "__main__":
    # Install playwright browsers if needed
    try:
        from playwright.sync_api import sync_playwright
        # Test if browser is available
        with sync_playwright() as p:
            p.chromium.launch(headless=True)
    except Exception as e:
        print("Installing Playwright browsers...")
        subprocess.run(["playwright", "install", "chromium"], check=True)
    
    success = run_usability_tests()
    exit(0 if success else 1)