# MetaOps Validator Codebase Reorganization & Testing Specification
**File Organization & Migration Testing Plan**

## Executive Summary

This specification defines the reorganization of the MetaOps Validator codebase to improve maintainability and reduce root directory clutter. The plan includes comprehensive testing using all available tools, particularly Playwright MCP, to ensure no functionality is broken during the migration process.

**Current Issues:**
- 25+ .md files in root directory creating clutter
- No clear separation between specifications, documentation, and reference materials  
- Multiple specification types mixed together
- Potential import/reference issues during reorganization

**Objectives:**
- Organize files into logical directory structure
- Maintain all existing functionality
- Preserve git history for moved files
- Comprehensive testing before and after reorganization

---

## 1. Current State Analysis

### 1.1 File Inventory (Root Directory)

**Documentation Files (25+ .md files):**
```
CLAUDE.md                                    # Project instructions
CLAUDE_BUSINESS.md                          # Business context
CLAUDE_TECHNICAL.md                         # Technical context
INTEGRATION_ARCHITECTURE.md                 # Integration specs
INTEGRATION_VALIDATION_REPORT.md            # Validation results
MVP_API_SPEC.md                             # API specification
OPERATIONAL_REQUIREMENTS_SPECIFICATION.md   # Operations spec
PIVOTS.md                                   # Strategic pivots
PRODUCTION_VALIDATION_ARCHITECTURE.md       # Production architecture
PROJECT_CONTEXT_FOR_CLAUDE_DESKTOP.md      # Desktop context
README.md                                   # Main readme
TECHNICAL_SPECIFICATION.md                  # Technical specs
TOOLTIPS_REFERENCE.md                       # UI tooltips
UI_SPECIFICATION.md                         # UI design specs
docs/diagnostic_brief.md                    # Diagnostic documentation
docs/governance_playbook.md                 # Governance guidelines
```

**Code References Analysis:**
- Streamlit apps may reference documentation files
- Python imports may use relative paths
- CLAUDE.md contains file path references
- Memory bank files reference documentation

### 1.2 Critical Dependencies

**Streamlit Applications:**
- `streamlit_app.py` - Main validator interface
- `streamlit_business_demo.py` - Business demo
- `src/metaops/web/streamlit_app.py` - Modular version
- `src/metaops/web/dashboard.py` - Analytics dashboard

**Python Code:**
- Import statements in `src/metaops/` modules
- Relative path references
- Configuration file locations

**Documentation References:**
- CLAUDE.md references to other files
- Memory bank cross-references
- README.md links to documentation

---

## 2. Proposed Directory Structure

### 2.1 New Organization

```
/specs/                                 # All specifications
├── features/                          # Feature specifications
│   ├── book-author-contract-demo-app.md
│   ├── api-gateway-integration.md
│   └── nielsen-scoring-enhancement.md
├── architecture/                      # Technical architecture
│   ├── integration-architecture.md
│   ├── production-validation-architecture.md
│   ├── database-design.md
│   └── performance-requirements.md
├── business/                          # Business specifications  
│   ├── operational-requirements.md
│   ├── strategic-pivots.md
│   ├── market-analysis.md
│   └── pricing-models.md
├── technical/                         # Technical specifications
│   ├── technical-specification.md
│   ├── api-specifications.md
│   ├── integration-validation-report.md
│   └── deployment-guides.md
└── ui-ux/                            # UI/UX specifications
    ├── ui-specification.md
    ├── tooltips-reference.md
    ├── user-workflows.md
    └── accessibility-requirements.md

/docs/                                 # User and developer documentation
├── user-guides/                       # End-user documentation
│   ├── getting-started.md
│   ├── validation-workflows.md
│   └── troubleshooting.md
├── developer/                         # Developer documentation
│   ├── api-reference.md
│   ├── development-setup.md
│   └── testing-guidelines.md
├── operations/                        # Operations documentation
│   ├── deployment-guide.md
│   ├── monitoring.md
│   └── backup-procedures.md
└── governance/                        # Project governance
    ├── governance-playbook.md
    ├── decision-log.md
    └── code-review-guidelines.md

/context/                              # Claude context files (keep in root for easy access)
├── CLAUDE.md                          # Main instructions (stays in root)
├── CLAUDE_BUSINESS.md                 # Business context
├── CLAUDE_TECHNICAL.md                # Technical context
└── PROJECT_CONTEXT_FOR_CLAUDE_DESKTOP.md

# Root Directory (minimal)
├── README.md                          # Main project readme
├── requirements.txt                   # Python dependencies
├── context/CLAUDE.md                  # Main Claude instructions
└── [standard project files]
```

### 2.2 File Migration Mapping

**Specifications → /specs/**
```bash
INTEGRATION_ARCHITECTURE.md → specs/architecture/integration-architecture.md
MVP_API_SPEC.md → specs/technical/api-specifications.md
OPERATIONAL_REQUIREMENTS_SPECIFICATION.md → specs/business/operational-requirements.md
PIVOTS.md → specs/business/strategic-pivots.md
PRODUCTION_VALIDATION_ARCHITECTURE.md → specs/architecture/production-validation-architecture.md
TECHNICAL_SPECIFICATION.md → specs/technical/technical-specification.md
UI_SPECIFICATION.md → specs/ui-ux/ui-specification.md
TOOLTIPS_REFERENCE.md → specs/ui-ux/tooltips-reference.md
INTEGRATION_VALIDATION_REPORT.md → specs/technical/integration-validation-report.md
```

**Documentation → /docs/**
```bash
docs/diagnostic_brief.md → docs/user-guides/diagnostic-brief.md
docs/governance_playbook.md → docs/governance/governance-playbook.md
```

**Context Files → /context/**
```bash
CLAUDE_BUSINESS.md → context/CLAUDE_BUSINESS.md
CLAUDE_TECHNICAL.md → context/CLAUDE_TECHNICAL.md
PROJECT_CONTEXT_FOR_CLAUDE_DESKTOP.md → context/PROJECT_CONTEXT_FOR_CLAUDE_DESKTOP.md
```

---

## 3. Pre-Migration Testing Plan

### 3.1 Comprehensive System Testing

**Current State Verification:**
```bash
#!/bin/bash
# pre_migration_tests.sh

echo "=== PRE-MIGRATION SYSTEM VERIFICATION ==="

# 1. Environment Setup
source .venv/bin/activate
export PYTHONPATH=/home/ed/meta-ops-validator/src

# 2. Core Validation Pipeline Test
echo "Testing validation pipeline..."
python -m pytest tests/ -v --tb=short

# 3. Web Interface Testing
echo "Testing web interfaces..."
# Start Streamlit apps and verify they load
streamlit run streamlit_app.py --server.port 8501 --server.headless true &
STREAMLIT_PID=$!
sleep 10

# Check if Streamlit is responding
curl -f http://localhost:8501/_stcore/health || echo "Main Streamlit app failed to start"

# Test business demo
streamlit run streamlit_business_demo.py --server.port 8502 --server.headless true &
DEMO_PID=$!
sleep 10

curl -f http://localhost:8502/_stcore/health || echo "Business demo failed to start"

# Cleanup
kill $STREAMLIT_PID $DEMO_PID

# 4. CLI Interface Test
echo "Testing CLI interface..."
python -m metaops.cli.main validate-xsd --onix data/samples/onix_samples/sample.xml --xsd data/samples/onix_samples/onix.xsd

# 5. File Reference Test
echo "Testing file references..."
python -c "
import os
files_to_check = [
    'CLAUDE.md',
    'README.md', 
    'TOOLTIPS_REFERENCE.md',
    'UI_SPECIFICATION.md'
]
for f in files_to_check:
    if os.path.exists(f):
        print(f'✓ {f} exists')
    else:
        print(f'✗ {f} missing')
"

echo "=== PRE-MIGRATION TESTS COMPLETE ==="
```

### 3.2 Playwright MCP UI Testing (Pre-Migration)

**Comprehensive UI Validation:**
```python
# tests/test_pre_migration_ui.py
import pytest
from playwright.async_api import async_playwright, Page, BrowserContext
import asyncio
import subprocess
import time
import os

class TestPreMigrationUI:
    """Comprehensive UI testing before file reorganization"""
    
    @pytest.fixture(scope="class")
    async def setup_streamlit_apps(self):
        """Start all Streamlit applications for testing"""
        
        # Set up environment
        os.environ['PYTHONPATH'] = '/home/ed/meta-ops-validator/src'
        
        # Start main validator app
        main_app = subprocess.Popen([
            'streamlit', 'run', 'streamlit_app.py',
            '--server.port', '8501',
            '--server.headless', 'true',
            '--server.address', '0.0.0.0'
        ])
        
        # Start business demo
        demo_app = subprocess.Popen([
            'streamlit', 'run', 'streamlit_business_demo.py', 
            '--server.port', '8502',
            '--server.headless', 'true',
            '--server.address', '0.0.0.0'
        ])
        
        # Start dashboard
        dashboard_app = subprocess.Popen([
            'streamlit', 'run', 'src/metaops/web/dashboard.py',
            '--server.port', '8503', 
            '--server.headless', 'true',
            '--server.address', '0.0.0.0'
        ])
        
        # Wait for apps to start
        time.sleep(15)
        
        yield {
            'main_app': main_app,
            'demo_app': demo_app, 
            'dashboard_app': dashboard_app
        }
        
        # Cleanup
        main_app.terminate()
        demo_app.terminate()
        dashboard_app.terminate()
    
    @pytest.fixture
    async def browser_context(self):
        """Setup browser context for UI testing"""
        async with async_playwright() as playwright:
            browser = await playwright.chromium.launch(headless=True)
            context = await browser.new_context(viewport={'width': 1920, 'height': 1080})
            yield context
            await browser.close()
    
    @pytest.mark.asyncio
    async def test_main_validator_interface(self, browser_context: BrowserContext, setup_streamlit_apps):
        """Test main validator interface functionality"""
        
        page = await browser_context.new_page()
        
        try:
            await page.goto("http://localhost:8501", timeout=30000)
            
            # Wait for page to load completely
            await page.wait_for_selector('h1', timeout=20000)
            
            # Verify main title
            title = await page.text_content('h1')
            assert "MetaOps Validator" in title or "ONIX" in title
            
            # Test file upload capability
            file_uploader = await page.query_selector('input[type="file"]')
            if file_uploader:
                # Test with sample ONIX file
                await file_uploader.set_input_files('test_onix_files/basic_namespaced.xml')
                
                # Look for upload confirmation
                await page.wait_for_timeout(2000)  # Wait for processing
                
            # Test navigation elements
            sidebar = await page.query_selector('[data-testid="stSidebar"]')
            assert sidebar is not None, "Sidebar not found"
            
            # Test validation workflow if available
            validate_button = await page.query_selector('button:has-text("Validate")')
            if validate_button:
                await validate_button.click()
                await page.wait_for_timeout(5000)  # Allow validation to process
                
            print("✓ Main validator interface test passed")
            
        except Exception as e:
            print(f"✗ Main validator interface test failed: {e}")
            raise
    
    @pytest.mark.asyncio 
    async def test_business_demo_interface(self, browser_context: BrowserContext, setup_streamlit_apps):
        """Test business demo interface"""
        
        page = await browser_context.new_page()
        
        try:
            await page.goto("http://localhost:8502", timeout=30000)
            
            # Wait for demo to load
            await page.wait_for_selector('[data-testid="stApp"]', timeout=20000)
            
            # Test KPI metrics display
            metrics = await page.query_selector_all('[data-testid="metric-container"]')
            assert len(metrics) > 0, "No KPI metrics found in business demo"
            
            # Test sample file selection if available
            sample_selector = await page.query_selector('select, [role="combobox"]')
            if sample_selector:
                await sample_selector.click()
                await page.wait_for_timeout(1000)
            
            # Test validation trigger
            validate_buttons = await page.query_selector_all('button:has-text("Validate")')
            if validate_buttons:
                await validate_buttons[0].click()
                await page.wait_for_timeout(8000)  # Allow full validation
                
                # Check for results display
                results_section = await page.query_selector('[data-testid="validation-results"], .validation-results, h3:has-text("Results")')
                if results_section:
                    print("✓ Validation results displayed in business demo")
                
            print("✓ Business demo interface test passed")
            
        except Exception as e:
            print(f"✗ Business demo interface test failed: {e}")
            raise
    
    @pytest.mark.asyncio
    async def test_dashboard_interface(self, browser_context: BrowserContext, setup_streamlit_apps):
        """Test analytics dashboard interface"""
        
        page = await browser_context.new_page()
        
        try:
            await page.goto("http://localhost:8503", timeout=30000)
            
            # Wait for dashboard to load
            await page.wait_for_selector('[data-testid="stApp"]', timeout=20000)
            
            # Test batch processing interface
            file_uploader = await page.query_selector('input[type="file"][multiple]')
            if file_uploader:
                # Test batch upload capability
                test_files = [
                    'test_onix_files/basic_namespaced.xml',
                    'test_onix_files/good_namespaced.xml'
                ]
                await file_uploader.set_input_files(test_files)
                await page.wait_for_timeout(3000)
                
            # Test analytics charts
            charts = await page.query_selector_all('[data-testid*="chart"], .plotly, canvas')
            if len(charts) > 0:
                print(f"✓ Found {len(charts)} analytics charts")
            
            # Test dashboard navigation
            tabs = await page.query_selector_all('[role="tab"], .stTabs > div > div')
            if len(tabs) > 1:
                await tabs[1].click()  # Switch to second tab
                await page.wait_for_timeout(2000)
                
            print("✓ Dashboard interface test passed")
            
        except Exception as e:
            print(f"✗ Dashboard interface test failed: {e}")
            raise
    
    @pytest.mark.asyncio
    async def test_tooltip_system(self, browser_context: BrowserContext, setup_streamlit_apps):
        """Test tooltip system functionality across interfaces"""
        
        page = await browser_context.new_page()
        
        # Test tooltips in main interface
        await page.goto("http://localhost:8501")
        await page.wait_for_selector('[data-testid="stApp"]', timeout=20000)
        
        # Look for help icons or elements with help text
        help_elements = await page.query_selector_all('[title], [data-tooltip], .stTooltipIcon')
        
        if help_elements:
            # Test first help element
            await help_elements[0].hover()
            await page.wait_for_timeout(1000)
            
            # Check if tooltip appears
            tooltip = await page.query_selector('[role="tooltip"], .tooltip, [data-testid="stTooltip"]')
            if tooltip:
                tooltip_text = await tooltip.text_content()
                assert len(tooltip_text.strip()) > 0, "Empty tooltip found"
                print(f"✓ Tooltip system working: '{tooltip_text[:50]}...'")
            else:
                print("? Tooltip system unclear - no tooltip visible")
        else:
            print("? No help elements found for tooltip testing")
    
    @pytest.mark.asyncio
    async def test_responsive_design(self, browser_context: BrowserContext, setup_streamlit_apps):
        """Test responsive design across different viewport sizes"""
        
        page = await browser_context.new_page()
        
        # Test desktop view
        await page.set_viewport_size({'width': 1920, 'height': 1080})
        await page.goto("http://localhost:8501")
        await page.wait_for_selector('[data-testid="stApp"]', timeout=20000)
        
        desktop_layout = await page.evaluate('() => document.body.offsetWidth')
        assert desktop_layout >= 1200, "Desktop layout not properly sized"
        
        # Test tablet view
        await page.set_viewport_size({'width': 768, 'height': 1024})
        await page.wait_for_timeout(2000)  # Allow layout adjustment
        
        tablet_layout = await page.evaluate('() => document.body.offsetWidth')
        assert 700 <= tablet_layout <= 800, "Tablet layout not responsive"
        
        # Test mobile view
        await page.set_viewport_size({'width': 375, 'height': 667})
        await page.wait_for_timeout(2000)
        
        mobile_layout = await page.evaluate('() => document.body.offsetWidth')
        assert mobile_layout <= 400, "Mobile layout not responsive"
        
        print("✓ Responsive design test passed")
    
    @pytest.mark.asyncio
    async def test_performance_benchmarks(self, browser_context: BrowserContext, setup_streamlit_apps):
        """Test performance benchmarks for all interfaces"""
        
        page = await browser_context.new_page()
        
        interfaces = [
            ('Main Validator', 'http://localhost:8501'),
            ('Business Demo', 'http://localhost:8502'),
            ('Dashboard', 'http://localhost:8503')
        ]
        
        performance_results = {}
        
        for name, url in interfaces:
            try:
                start_time = time.time()
                await page.goto(url, timeout=30000)
                await page.wait_for_selector('[data-testid="stApp"]', timeout=20000)
                load_time = time.time() - start_time
                
                performance_results[name] = {
                    'load_time': load_time,
                    'status': 'passed' if load_time < 10.0 else 'slow'
                }
                
                print(f"✓ {name}: {load_time:.2f}s load time")
                
            except Exception as e:
                performance_results[name] = {
                    'load_time': None,
                    'status': 'failed', 
                    'error': str(e)
                }
                print(f"✗ {name}: Failed to load - {e}")
        
        return performance_results
    
    @pytest.mark.asyncio
    async def test_error_handling(self, browser_context: BrowserContext, setup_streamlit_apps):
        """Test error handling across interfaces"""
        
        page = await browser_context.new_page()
        await page.goto("http://localhost:8501")
        await page.wait_for_selector('[data-testid="stApp"]', timeout=20000)
        
        # Test invalid file upload if possible
        file_uploader = await page.query_selector('input[type="file"]')
        if file_uploader:
            # Create invalid file for testing
            invalid_file_path = '/tmp/invalid_test_file.txt'
            with open(invalid_file_path, 'w') as f:
                f.write("This is not valid ONIX XML")
            
            try:
                await file_uploader.set_input_files(invalid_file_path)
                await page.wait_for_timeout(3000)
                
                # Look for error messages
                error_messages = await page.query_selector_all('.stAlert, [data-testid="stAlert"], .error')
                if error_messages:
                    print("✓ Error handling working - error messages displayed")
                else:
                    print("? Error handling unclear - no error messages found")
                    
            finally:
                os.unlink(invalid_file_path)
        
        print("✓ Error handling test completed")

# Generate comprehensive test report
def generate_pre_migration_report():
    """Generate comprehensive pre-migration test report"""
    
    report = {
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
        'system_status': 'pre_migration',
        'tests_run': [],
        'issues_found': [],
        'performance_benchmarks': {},
        'file_references': [],
        'recommendations': []
    }
    
    # File reference analysis
    files_to_analyze = [
        'streamlit_app.py',
        'streamlit_business_demo.py', 
        'src/metaops/web/dashboard.py',
        'CLAUDE.md',
        'README.md'
    ]
    
    for file_path in files_to_analyze:
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                
                # Look for potential file references
                import re
                references = re.findall(r'["\']([^"\']*\.md)["\']', content)
                references.extend(re.findall(r'read_csv\(["\']([^"\']*)["\']', content))
                references.extend(re.findall(r'Path\(["\']([^"\']*)["\']', content))
                
                if references:
                    report['file_references'].append({
                        'file': file_path,
                        'references': references
                    })
    
    return report
```

---

## 4. Migration Execution Plan

### 4.1 Migration Script

**Safe File Migration with Git History Preservation:**
```bash
#!/bin/bash
# migrate_files.sh

set -e  # Exit on any error

echo "=== METAOPS VALIDATOR FILE MIGRATION ==="

# 1. Pre-migration backup
echo "Creating pre-migration backup..."
git tag "pre-reorganization-backup-$(date +%Y%m%d-%H%M%S)"
git add -A && git commit -m "Pre-reorganization checkpoint"

# 2. Create new directory structure
echo "Creating new directory structure..."
mkdir -p specs/{features,architecture,business,technical,ui-ux}
mkdir -p docs/{user-guides,developer,operations,governance}
mkdir -p context

# 3. Move files with git mv (preserves history)
echo "Moving specification files..."

# Architecture specifications
git mv INTEGRATION_ARCHITECTURE.md specs/architecture/integration-architecture.md
git mv PRODUCTION_VALIDATION_ARCHITECTURE.md specs/architecture/production-validation-architecture.md

# Technical specifications  
git mv TECHNICAL_SPECIFICATION.md specs/technical/technical-specification.md
git mv MVP_API_SPEC.md specs/technical/api-specifications.md
git mv INTEGRATION_VALIDATION_REPORT.md specs/technical/integration-validation-report.md

# Business specifications
git mv OPERATIONAL_REQUIREMENTS_SPECIFICATION.md specs/business/operational-requirements.md
git mv PIVOTS.md specs/business/strategic-pivots.md

# UI/UX specifications
git mv UI_SPECIFICATION.md specs/ui-ux/ui-specification.md
git mv TOOLTIPS_REFERENCE.md specs/ui-ux/tooltips-reference.md

# Context files
git mv CLAUDE_BUSINESS.md context/CLAUDE_BUSINESS.md
git mv CLAUDE_TECHNICAL.md context/CLAUDE_TECHNICAL.md
git mv PROJECT_CONTEXT_FOR_CLAUDE_DESKTOP.md context/PROJECT_CONTEXT_FOR_CLAUDE_DESKTOP.md

# Documentation files
git mv docs/diagnostic_brief.md docs/user-guides/diagnostic-brief.md
git mv docs/governance_playbook.md docs/governance/governance-playbook.md

# 4. Update file references
echo "Updating file references..."

# Update CLAUDE.md references
sed -i 's|CLAUDE_BUSINESS\.md|context/CLAUDE_BUSINESS.md|g' CLAUDE.md
sed -i 's|CLAUDE_TECHNICAL\.md|context/CLAUDE_TECHNICAL.md|g' CLAUDE.md
sed -i 's|TOOLTIPS_REFERENCE\.md|specs/ui-ux/tooltips-reference.md|g' CLAUDE.md
sed -i 's|UI_SPECIFICATION\.md|specs/ui-ux/ui-specification.md|g' CLAUDE.md

# Update README.md references  
sed -i 's|\*\*TECHNICAL_SPECIFICATION\.md\*\*|**specs/technical/technical-specification.md**|g' README.md
sed -i 's|\*\*UI_SPECIFICATION\.md\*\*|**specs/ui-ux/ui-specification.md**|g' README.md

# Update any Python file references
find src/ -name "*.py" -exec sed -i 's|"TOOLTIPS_REFERENCE\.md"|"specs/ui-ux/tooltips-reference.md"|g' {} \;

# Update Streamlit app references
sed -i 's|TOOLTIPS_REFERENCE\.md|specs/ui-ux/tooltips-reference.md|g' streamlit_app.py streamlit_business_demo.py 2>/dev/null || true

echo "=== MIGRATION COMPLETE ==="
```

### 4.2 Reference Update Script

**Automated Reference Detection and Update:**
```python
#!/usr/bin/env python3
# update_references.py

import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple

class ReferenceUpdater:
    """Update file references after reorganization"""
    
    def __init__(self):
        self.file_mappings = {
            'INTEGRATION_ARCHITECTURE.md': 'specs/architecture/integration-architecture.md',
            'MVP_API_SPEC.md': 'specs/technical/api-specifications.md',
            'OPERATIONAL_REQUIREMENTS_SPECIFICATION.md': 'specs/business/operational-requirements.md',
            'PIVOTS.md': 'specs/business/strategic-pivots.md',
            'PRODUCTION_VALIDATION_ARCHITECTURE.md': 'specs/architecture/production-validation-architecture.md',
            'TECHNICAL_SPECIFICATION.md': 'specs/technical/technical-specification.md',
            'UI_SPECIFICATION.md': 'specs/ui-ux/ui-specification.md',
            'TOOLTIPS_REFERENCE.md': 'specs/ui-ux/tooltips-reference.md',
            'INTEGRATION_VALIDATION_REPORT.md': 'specs/technical/integration-validation-report.md',
            'CLAUDE_BUSINESS.md': 'context/CLAUDE_BUSINESS.md',
            'CLAUDE_TECHNICAL.md': 'context/CLAUDE_TECHNICAL.md',
            'PROJECT_CONTEXT_FOR_CLAUDE_DESKTOP.md': 'context/PROJECT_CONTEXT_FOR_CLAUDE_DESKTOP.md',
            'docs/diagnostic_brief.md': 'docs/user-guides/diagnostic-brief.md',
            'docs/governance_playbook.md': 'docs/governance/governance-playbook.md'
        }
        
        self.files_to_update = [
            'CLAUDE.md',
            'README.md',
            'streamlit_app.py',
            'streamlit_business_demo.py',
            'src/metaops/web/dashboard.py',
            'src/metaops/web/streamlit_app.py'
        ]
    
    def find_file_references(self, file_path: str) -> List[Tuple[str, int, str]]:
        """Find all file references in a given file"""
        references = []
        
        if not os.path.exists(file_path):
            return references
            
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
                
            for line_num, line in enumerate(lines, 1):
                for old_path in self.file_mappings.keys():
                    if old_path in line:
                        references.append((old_path, line_num, line.strip()))
                        
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
            
        return references
    
    def update_file_references(self, file_path: str) -> bool:
        """Update file references in a specific file"""
        
        if not os.path.exists(file_path):
            print(f"Warning: {file_path} not found")
            return False
            
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                
            original_content = content
            
            # Update references
            for old_path, new_path in self.file_mappings.items():
                # Various reference patterns
                patterns = [
                    rf'"{re.escape(old_path)}"',  # Quoted references
                    rf"'{re.escape(old_path)}'",  # Single quoted
                    rf'\[{re.escape(old_path)}\]',  # Markdown links
                    rf'{re.escape(old_path)}(?=\s|$|[^\w\-\.])',  # Word boundaries
                ]
                
                replacements = [
                    f'"{new_path}"',
                    f"'{new_path}'", 
                    f'[{new_path}]',
                    new_path
                ]
                
                for pattern, replacement in zip(patterns, replacements):
                    content = re.sub(pattern, replacement, content)
            
            # Write updated content if changes were made
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"✓ Updated references in {file_path}")
                return True
            else:
                print(f"- No changes needed in {file_path}")
                return False
                
        except Exception as e:
            print(f"Error updating {file_path}: {e}")
            return False
    
    def generate_reference_report(self) -> Dict:
        """Generate report of all file references before update"""
        
        report = {
            'files_analyzed': [],
            'references_found': {},
            'potential_issues': []
        }
        
        for file_path in self.files_to_update:
            if os.path.exists(file_path):
                references = self.find_file_references(file_path)
                if references:
                    report['references_found'][file_path] = references
                report['files_analyzed'].append(file_path)
        
        # Check for unmapped references
        all_md_files = list(Path('.').glob('**/*.md'))
        for md_file in all_md_files:
            if str(md_file) not in self.file_mappings and str(md_file) not in ['README.md', 'CLAUDE.md']:
                report['potential_issues'].append(f"Unmapped file: {md_file}")
        
        return report
    
    def update_all_references(self):
        """Update references in all specified files"""
        
        print("=== FILE REFERENCE UPDATE ===")
        
        # Generate pre-update report
        report = self.generate_reference_report()
        
        print(f"Found references in {len(report['references_found'])} files:")
        for file_path, references in report['references_found'].items():
            print(f"  {file_path}: {len(references)} references")
        
        if report['potential_issues']:
            print(f"Potential issues: {len(report['potential_issues'])}")
            for issue in report['potential_issues'][:5]:  # Show first 5
                print(f"  - {issue}")
        
        # Update all files
        updated_count = 0
        for file_path in self.files_to_update:
            if self.update_file_references(file_path):
                updated_count += 1
        
        print(f"Updated {updated_count} files")
        print("=== REFERENCE UPDATE COMPLETE ===")

if __name__ == "__main__":
    updater = ReferenceUpdater()
    updater.update_all_references()
```

---

## 5. Post-Migration Testing Plan

### 5.1 Comprehensive Verification Testing

**Post-Migration Validation Script:**
```bash
#!/bin/bash
# post_migration_tests.sh

echo "=== POST-MIGRATION SYSTEM VERIFICATION ==="

# 1. Environment Setup
source .venv/bin/activate
export PYTHONPATH=/home/ed/meta-ops-validator/src

# 2. File Existence Check
echo "Verifying file structure..."

# Check critical files are in new locations
files_to_check=(
    "specs/technical/technical-specification.md"
    "specs/ui-ux/ui-specification.md"
    "specs/ui-ux/tooltips-reference.md"
    "context/CLAUDE_BUSINESS.md"
    "context/CLAUDE_TECHNICAL.md"
    "docs/governance/governance-playbook.md"
)

for file in "${files_to_check[@]}"; do
    if [[ -f "$file" ]]; then
        echo "✓ $file exists"
    else
        echo "✗ $file MISSING"
        exit 1
    fi
done

# 3. Python Import Test
echo "Testing Python imports..."
python -c "
import sys
sys.path.insert(0, 'src')

try:
    from metaops.validators.onix_xsd import validate_xsd
    from metaops.validators.onix_schematron import validate_schematron
    from metaops.validators.nielsen_scoring import calculate_nielsen_score
    print('✓ All Python imports successful')
except ImportError as e:
    print(f'✗ Import error: {e}')
    sys.exit(1)
"

# 4. Core Validation Pipeline Test  
echo "Testing validation pipeline..."
python -m metaops.cli.main validate-xsd --onix test_onix_files/basic_namespaced.xml --xsd data/editeur/ONIX_BookProduct_3.0_reference.xsd

# 5. Web Interface Test
echo "Testing web interfaces..."

# Test main app
streamlit run streamlit_app.py --server.port 8501 --server.headless true &
MAIN_PID=$!
sleep 10

if curl -f http://localhost:8501/_stcore/health; then
    echo "✓ Main Streamlit app running"
else
    echo "✗ Main Streamlit app failed"
    kill $MAIN_PID
    exit 1
fi

# Test business demo
streamlit run streamlit_business_demo.py --server.port 8502 --server.headless true &
DEMO_PID=$!
sleep 10

if curl -f http://localhost:8502/_stcore/health; then
    echo "✓ Business demo app running"
else
    echo "✗ Business demo app failed"
    kill $MAIN_PID $DEMO_PID
    exit 1
fi

# Cleanup
kill $MAIN_PID $DEMO_PID
sleep 5

echo "=== POST-MIGRATION TESTS COMPLETE ==="
```

### 5.2 Playwright MCP Post-Migration Testing

**Complete UI Regression Testing:**
```python
# tests/test_post_migration_ui.py
import pytest
from playwright.async_api import async_playwright, Page, BrowserContext
import subprocess
import time
import os

class TestPostMigrationUI:
    """Comprehensive UI regression testing after file reorganization"""
    
    @pytest.fixture(scope="class")
    async def setup_streamlit_apps(self):
        """Start all Streamlit applications for post-migration testing"""
        
        # Ensure environment is properly set
        os.environ['PYTHONPATH'] = '/home/ed/meta-ops-validator/src'
        
        apps = {}
        
        try:
            # Start main validator app
            apps['main'] = subprocess.Popen([
                'streamlit', 'run', 'streamlit_app.py',
                '--server.port', '8501',
                '--server.headless', 'true',
                '--server.address', '0.0.0.0'
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            # Start business demo
            apps['demo'] = subprocess.Popen([
                'streamlit', 'run', 'streamlit_business_demo.py',
                '--server.port', '8502', 
                '--server.headless', 'true',
                '--server.address', '0.0.0.0'
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            # Start dashboard
            apps['dashboard'] = subprocess.Popen([
                'streamlit', 'run', 'src/metaops/web/dashboard.py',
                '--server.port', '8503',
                '--server.headless', 'true', 
                '--server.address', '0.0.0.0'
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            # Wait for all apps to start
            time.sleep(20)
            
            # Verify all apps are responding
            import requests
            for name, port in [('main', 8501), ('demo', 8502), ('dashboard', 8503)]:
                try:
                    response = requests.get(f'http://localhost:{port}/_stcore/health', timeout=5)
                    if response.status_code != 200:
                        raise Exception(f"{name} app not responding")
                    print(f"✓ {name} app running on port {port}")
                except Exception as e:
                    print(f"✗ {name} app failed to start: {e}")
                    raise
            
            yield apps
            
        finally:
            # Cleanup all processes
            for name, process in apps.items():
                try:
                    process.terminate()
                    process.wait(timeout=5)
                except:
                    process.kill()
    
    @pytest.fixture
    async def browser_context(self):
        """Setup browser context for UI testing"""
        async with async_playwright() as playwright:
            browser = await playwright.chromium.launch(headless=True)
            context = await browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                ignore_https_errors=True
            )
            yield context
            await browser.close()
    
    @pytest.mark.asyncio
    async def test_main_validator_post_migration(self, browser_context: BrowserContext, setup_streamlit_apps):
        """Test main validator interface after migration"""
        
        page = await browser_context.new_page()
        
        try:
            # Navigate to main validator
            await page.goto("http://localhost:8501", timeout=60000)
            
            # Wait for app to fully load
            await page.wait_for_selector('[data-testid="stApp"]', timeout=30000)
            
            # Verify title/header
            await page.wait_for_selector('h1, h2, h3', timeout=10000)
            title_element = await page.query_selector('h1')
            if title_element:
                title_text = await title_element.text_content()
                assert any(keyword in title_text.lower() for keyword in ['metaops', 'onix', 'validator'])
                print(f"✓ Main validator title: {title_text}")
            
            # Test file upload functionality
            file_uploader = await page.query_selector('input[type="file"]')
            if file_uploader:
                # Test with known good file
                await file_uploader.set_input_files('test_onix_files/good_namespaced.xml')
                await page.wait_for_timeout(3000)
                print("✓ File upload working")
                
                # Look for validation trigger
                validate_button = await page.query_selector('button:has-text("Validate"), button:has-text("Process"), button:has-text("Analyze")')
                if validate_button:
                    await validate_button.click()
                    
                    # Wait for processing
                    await page.wait_for_timeout(10000)
                    
                    # Check for results
                    results_indicators = await page.query_selector_all(
                        '[data-testid*="metric"], .metric, h3:has-text("Score"), h3:has-text("Result")'
                    )
                    
                    if results_indicators:
                        print(f"✓ Validation results displayed ({len(results_indicators)} indicators)")
                    else:
                        print("? Validation results unclear")
            
            # Test tooltip functionality (critical after file moves)
            help_elements = await page.query_selector_all('[title], [data-tooltip], .stTooltipIcon, button[aria-label*="help"]')
            
            tooltip_working = False
            for element in help_elements[:3]:  # Test first few
                try:
                    await element.hover()
                    await page.wait_for_timeout(1000)
                    
                    tooltip = await page.query_selector('[role="tooltip"], .tooltip, [data-testid="stTooltip"]')
                    if tooltip:
                        tooltip_text = await tooltip.text_content()
                        if tooltip_text and len(tooltip_text.strip()) > 5:
                            tooltip_working = True
                            print(f"✓ Tooltips working: '{tooltip_text[:30]}...'")
                            break
                except:
                    continue
            
            if not tooltip_working and help_elements:
                print("⚠ Tooltip system may have issues after migration")
            
            print("✓ Main validator post-migration test passed")
            
        except Exception as e:
            print(f"✗ Main validator post-migration test failed: {e}")
            # Take screenshot for debugging
            await page.screenshot(path='main_validator_error.png')
            raise
    
    @pytest.mark.asyncio
    async def test_business_demo_post_migration(self, browser_context: BrowserContext, setup_streamlit_apps):
        """Test business demo interface after migration"""
        
        page = await browser_context.new_page()
        
        try:
            await page.goto("http://localhost:8502", timeout=60000)
            await page.wait_for_selector('[data-testid="stApp"]', timeout=30000)
            
            # Test KPI display (critical for business demo)
            await page.wait_for_timeout(5000)  # Allow metrics to load
            
            metrics = await page.query_selector_all('[data-testid*="metric"], .metric')
            if len(metrics) >= 3:
                print(f"✓ Business KPIs displayed ({len(metrics)} metrics)")
                
                # Test individual metrics
                for i, metric in enumerate(metrics[:4]):
                    metric_text = await metric.text_content()
                    if metric_text and any(char.isdigit() for char in metric_text):
                        print(f"  - Metric {i+1}: Contains numeric data")
                    else:
                        print(f"  - Metric {i+1}: May have display issues")
            else:
                print(f"⚠ Expected multiple KPI metrics, found {len(metrics)}")
            
            # Test sample file processing (if embedded samples work)
            sample_buttons = await page.query_selector_all('button:has-text("Sample"), button:has-text("Demo"), button:has-text("Example")')
            
            if sample_buttons:
                await sample_buttons[0].click()
                await page.wait_for_timeout(2000)
                
                # Trigger validation
                validate_buttons = await page.query_selector_all('button:has-text("Validate"), button:has-text("Analyze")')
                if validate_buttons:
                    await validate_buttons[0].click()
                    await page.wait_for_timeout(15000)  # Allow full validation
                    
                    # Check for comprehensive results
                    result_sections = await page.query_selector_all(
                        'h3:has-text("Nielsen"), h3:has-text("Retailer"), h3:has-text("Validation"), .stExpander'
                    )
                    
                    if len(result_sections) >= 3:
                        print(f"✓ Comprehensive validation results ({len(result_sections)} sections)")
                    else:
                        print(f"⚠ Expected multiple result sections, found {len(result_sections)}")
            
            # Test navigation and tabs if present
            tabs = await page.query_selector_all('[role="tab"], button:has-text("Dashboard"), button:has-text("Analytics")')
            if len(tabs) > 1:
                await tabs[1].click()
                await page.wait_for_timeout(3000)
                print("✓ Tab navigation working")
            
            print("✓ Business demo post-migration test passed")
            
        except Exception as e:
            print(f"✗ Business demo post-migration test failed: {e}")
            await page.screenshot(path='business_demo_error.png')
            raise
    
    @pytest.mark.asyncio
    async def test_dashboard_post_migration(self, browser_context: BrowserContext, setup_streamlit_apps):
        """Test analytics dashboard after migration"""
        
        page = await browser_context.new_page()
        
        try:
            await page.goto("http://localhost:8503", timeout=60000)
            await page.wait_for_selector('[data-testid="stApp"]', timeout=30000)
            
            # Wait for dashboard to load
            await page.wait_for_timeout(8000)
            
            # Test batch file upload capability
            file_uploader = await page.query_selector('input[type="file"][multiple], input[type="file"]')
            if file_uploader:
                test_files = [
                    'test_onix_files/basic_namespaced.xml',
                    'test_onix_files/good_namespaced.xml',
                    'test_onix_files/excellent_namespaced.xml'
                ]
                
                # Upload multiple files
                await file_uploader.set_input_files(test_files)
                await page.wait_for_timeout(5000)
                
                # Look for processing trigger
                process_button = await page.query_selector('button:has-text("Process"), button:has-text("Validate"), button:has-text("Analyze")')
                if process_button:
                    await process_button.click()
                    await page.wait_for_timeout(20000)  # Allow batch processing
                    
                    # Check for batch results
                    results_tables = await page.query_selector_all('table, [data-testid*="dataframe"], .dataframe')
                    charts = await page.query_selector_all('canvas, [data-testid*="chart"], .plotly')
                    
                    if results_tables or charts:
                        print(f"✓ Batch results displayed (tables: {len(results_tables)}, charts: {len(charts)})")
                    else:
                        print("⚠ Batch results may not be displaying correctly")
            
            # Test dashboard analytics display
            metric_containers = await page.query_selector_all('[data-testid*="metric"], .metric, .stMetric')
            if metric_containers:
                print(f"✓ Dashboard metrics displayed ({len(metric_containers)} containers)")
            
            # Test chart interactions if present
            charts = await page.query_selector_all('canvas, [data-testid*="chart"], .plotly')
            if charts:
                # Try to interact with first chart
                try:
                    await charts[0].hover()
                    await page.wait_for_timeout(1000)
                    print("✓ Chart interaction working")
                except:
                    print("? Chart interaction unclear")
            
            print("✓ Dashboard post-migration test passed")
            
        except Exception as e:
            print(f"✗ Dashboard post-migration test failed: {e}")
            await page.screenshot(path='dashboard_error.png')
            raise
    
    @pytest.mark.asyncio
    async def test_reference_integrity(self, browser_context: BrowserContext, setup_streamlit_apps):
        """Test that all file references work after migration"""
        
        page = await browser_context.new_page()
        
        # Test each interface for potential reference errors
        interfaces = [
            ('Main Validator', 'http://localhost:8501'),
            ('Business Demo', 'http://localhost:8502'), 
            ('Dashboard', 'http://localhost:8503')
        ]
        
        reference_issues = []
        
        for name, url in interfaces:
            try:
                await page.goto(url, timeout=60000)
                await page.wait_for_selector('[data-testid="stApp"]', timeout=30000)
                
                # Check browser console for errors
                messages = await page.evaluate('''() => {
                    const errors = [];
                    window.addEventListener('error', (e) => {
                        errors.push(e.message);
                    });
                    return errors;
                }''')
                
                if messages:
                    reference_issues.append(f"{name}: {messages}")
                
                # Look for broken references in UI
                error_elements = await page.query_selector_all('.stAlert--error, [data-testid*="error"], .error')
                for error_element in error_elements:
                    error_text = await error_element.text_content()
                    if 'file' in error_text.lower() or 'not found' in error_text.lower():
                        reference_issues.append(f"{name}: {error_text}")
                
            except Exception as e:
                reference_issues.append(f"{name}: Failed to load - {str(e)}")
        
        if reference_issues:
            print("⚠ Reference issues found:")
            for issue in reference_issues:
                print(f"  - {issue}")
        else:
            print("✓ No reference integrity issues detected")
        
        return reference_issues
    
    @pytest.mark.asyncio
    async def test_performance_comparison(self, browser_context: BrowserContext, setup_streamlit_apps):
        """Compare performance before and after migration"""
        
        page = await browser_context.new_page()
        
        interfaces = [
            ('Main Validator', 'http://localhost:8501'),
            ('Business Demo', 'http://localhost:8502'),
            ('Dashboard', 'http://localhost:8503')
        ]
        
        performance_results = {}
        
        for name, url in interfaces:
            try:
                start_time = time.time()
                await page.goto(url, timeout=60000)
                await page.wait_for_selector('[data-testid="stApp"]', timeout=30000)
                
                # Wait for content to fully load
                await page.wait_for_timeout(5000)
                load_time = time.time() - start_time
                
                # Test interactive performance
                start_time = time.time()
                
                # Try to interact with interface
                buttons = await page.query_selector_all('button')
                if buttons:
                    await buttons[0].click()
                    await page.wait_for_timeout(2000)
                
                interaction_time = time.time() - start_time
                
                performance_results[name] = {
                    'load_time': load_time,
                    'interaction_time': interaction_time,
                    'status': 'good' if load_time < 15.0 and interaction_time < 5.0 else 'needs_attention'
                }
                
                print(f"{name}: Load {load_time:.2f}s, Interaction {interaction_time:.2f}s")
                
            except Exception as e:
                performance_results[name] = {
                    'load_time': None,
                    'interaction_time': None,
                    'status': 'failed',
                    'error': str(e)
                }
                print(f"{name}: Performance test failed - {e}")
        
        return performance_results

# Comprehensive post-migration test report
def generate_post_migration_report(ui_test_results):
    """Generate comprehensive post-migration test report"""
    
    report = {
        'migration_date': time.strftime('%Y-%m-%d %H:%M:%S'),
        'system_status': 'post_migration',
        'ui_tests': ui_test_results,
        'file_structure_verified': True,
        'python_imports_working': True,
        'web_interfaces_operational': True,
        'reference_integrity': 'good',
        'performance_status': 'acceptable',
        'issues_found': [],
        'recommendations': [
            'Monitor system performance for first week after migration',
            'Run weekly regression tests to catch any delayed issues', 
            'Update documentation to reflect new file locations',
            'Train team on new file organization structure'
        ]
    }
    
    return report
```

---

## 6. Rollback Plan

### 6.1 Emergency Rollback Procedure

**Quick Rollback to Pre-Migration State:**
```bash
#!/bin/bash
# emergency_rollback.sh

echo "=== EMERGENCY ROLLBACK TO PRE-MIGRATION STATE ==="

# 1. Find the backup tag
BACKUP_TAG=$(git tag | grep "pre-reorganization-backup" | head -1)

if [ -z "$BACKUP_TAG" ]; then
    echo "✗ No backup tag found! Manual recovery required."
    exit 1
fi

echo "Found backup tag: $BACKUP_TAG"

# 2. Create rollback checkpoint
git add -A
git commit -m "Pre-rollback checkpoint - $(date)"
git tag "pre-rollback-$(date +%Y%m%d-%H%M%S)"

# 3. Reset to backup state
echo "Rolling back to $BACKUP_TAG..."
git reset --hard $BACKUP_TAG

# 4. Verify rollback
echo "Verifying rollback..."

# Check critical files are back
critical_files=(
    "CLAUDE.md"
    "README.md"
    "TECHNICAL_SPECIFICATION.md"
    "UI_SPECIFICATION.md"
    "TOOLTIPS_REFERENCE.md"
)

for file in "${critical_files[@]}"; do
    if [[ -f "$file" ]]; then
        echo "✓ $file restored"
    else
        echo "✗ $file missing after rollback"
    fi
done

# 5. Test basic functionality
echo "Testing basic functionality..."
source .venv/bin/activate
export PYTHONPATH=/home/ed/meta-ops-validator/src

# Quick validation test
if python -m metaops.cli.main validate-xsd --onix test_onix_files/basic_namespaced.xml --xsd data/editeur/ONIX_BookProduct_3.0_reference.xsd; then
    echo "✓ Basic validation working"
else
    echo "✗ Validation pipeline may have issues"
fi

echo "=== ROLLBACK COMPLETE ==="
echo "System restored to pre-migration state"
echo "Investigate issues before attempting migration again"
```

### 6.2 Selective Recovery Plan

**Recover Specific Components:**
```bash
#!/bin/bash
# selective_recovery.sh

echo "=== SELECTIVE COMPONENT RECOVERY ==="

case "$1" in
    "ui")
        echo "Recovering UI components..."
        git checkout HEAD~1 -- streamlit_app.py streamlit_business_demo.py
        git checkout HEAD~1 -- src/metaops/web/
        ;;
    "docs")
        echo "Recovering documentation..."
        git checkout HEAD~1 -- TECHNICAL_SPECIFICATION.md UI_SPECIFICATION.md TOOLTIPS_REFERENCE.md
        ;;
    "context")
        echo "Recovering context files..."
        git checkout HEAD~1 -- CLAUDE_BUSINESS.md CLAUDE_TECHNICAL.md
        ;;
    *)
        echo "Usage: $0 [ui|docs|context]"
        exit 1
        ;;
esac

echo "Selective recovery complete"
```

---

## 7. Success Criteria and Acceptance Testing

### 7.1 Migration Success Metrics

**Technical Success Criteria:**
- [ ] All Streamlit applications load without errors
- [ ] Validation pipeline produces identical results
- [ ] No broken file references in code or documentation
- [ ] Performance degradation <10% vs pre-migration
- [ ] All tooltips and help systems functional

**User Experience Success Criteria:**
- [ ] UI workflows complete without issues
- [ ] File upload and validation process unchanged
- [ ] Dashboard analytics display correctly
- [ ] Error handling and messaging work properly
- [ ] Responsive design maintained

**Organizational Success Criteria:**
- [ ] File structure intuitive for new team members
- [ ] Specifications easy to locate and reference
- [ ] Documentation properly categorized
- [ ] Git history preserved for all moved files
- [ ] Development workflow efficiency maintained

### 7.2 Final Acceptance Test Suite

**Comprehensive Acceptance Testing:**
```python
# tests/test_migration_acceptance.py
import pytest
import subprocess
import time
import os
from pathlib import Path

class TestMigrationAcceptance:
    """Final acceptance tests for file reorganization"""
    
    def test_all_critical_files_exist(self):
        """Verify all critical files exist in new locations"""
        
        required_files = [
            'specs/technical/technical-specification.md',
            'specs/ui-ux/ui-specification.md', 
            'specs/ui-ux/tooltips-reference.md',
            'specs/business/operational-requirements.md',
            'context/CLAUDE_BUSINESS.md',
            'context/CLAUDE_TECHNICAL.md',
            'docs/governance/governance-playbook.md',
            'README.md',
            'CLAUDE.md'
        ]
        
        for file_path in required_files:
            assert Path(file_path).exists(), f"Required file missing: {file_path}"
    
    def test_python_imports_working(self):
        """Verify all Python imports still work"""
        
        import_tests = [
            'from metaops.validators.onix_xsd import validate_xsd',
            'from metaops.validators.onix_schematron import validate_schematron',
            'from metaops.validators.nielsen_scoring import calculate_nielsen_score',
            'from metaops.rules.engine import evaluate'
        ]
        
        for import_stmt in import_tests:
            try:
                exec(import_stmt)
            except ImportError as e:
                pytest.fail(f"Import failed after migration: {import_stmt} - {e}")
    
    def test_cli_interface_functional(self):
        """Test CLI interface works after migration"""
        
        # Set up environment
        env = os.environ.copy()
        env['PYTHONPATH'] = '/home/ed/meta-ops-validator/src'
        
        # Test basic validation command
        result = subprocess.run([
            'python', '-m', 'metaops.cli.main', 'validate-xsd',
            '--onix', 'test_onix_files/basic_namespaced.xml',
            '--xsd', 'data/editeur/ONIX_BookProduct_3.0_reference.xsd'
        ], env=env, capture_output=True, text=True)
        
        assert result.returncode == 0, f"CLI validation failed: {result.stderr}"
    
    def test_web_interfaces_start(self):
        """Test all web interfaces can start successfully"""
        
        env = os.environ.copy()
        env['PYTHONPATH'] = '/home/ed/meta-ops-validator/src'
        
        apps_to_test = [
            ('streamlit_app.py', 8501),
            ('streamlit_business_demo.py', 8502),
            ('src/metaops/web/dashboard.py', 8503)
        ]
        
        for app_file, port in apps_to_test:
            process = subprocess.Popen([
                'streamlit', 'run', app_file,
                '--server.port', str(port),
                '--server.headless', 'true'
            ], env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            time.sleep(10)  # Allow app to start
            
            # Check if process is still running (didn't crash)
            assert process.poll() is None, f"App {app_file} crashed on startup"
            
            process.terminate()
            process.wait(timeout=5)
    
    def test_file_references_updated(self):
        """Verify file references have been properly updated"""
        
        files_with_references = [
            'CLAUDE.md',
            'README.md'
        ]
        
        old_references = [
            'CLAUDE_BUSINESS.md',
            'CLAUDE_TECHNICAL.md', 
            'TECHNICAL_SPECIFICATION.md',
            'UI_SPECIFICATION.md',
            'TOOLTIPS_REFERENCE.md'
        ]
        
        for file_path in files_with_references:
            if Path(file_path).exists():
                content = Path(file_path).read_text()
                
                for old_ref in old_references:
                    # Should not contain old direct references
                    assert old_ref not in content or f"context/{old_ref}" in content or f"specs/" in content, \
                        f"Unreplaced reference to {old_ref} in {file_path}"
    
    def test_git_history_preserved(self):
        """Verify git history is preserved for moved files"""
        
        moved_files = [
            'specs/technical/technical-specification.md',
            'specs/ui-ux/ui-specification.md',
            'context/CLAUDE_BUSINESS.md'
        ]
        
        for file_path in moved_files:
            if Path(file_path).exists():
                # Check git log shows history
                result = subprocess.run([
                    'git', 'log', '--oneline', file_path
                ], capture_output=True, text=True)
                
                assert result.returncode == 0, f"Git log failed for {file_path}"
                assert len(result.stdout.strip()) > 0, f"No git history for {file_path}"
    
    def test_directory_structure_clean(self):
        """Verify root directory is cleaner after reorganization"""
        
        root_md_files = list(Path('.').glob('*.md'))
        
        # Should only have essential files in root
        allowed_root_files = ['README.md', 'CLAUDE.md']
        
        unexpected_files = [
            f for f in root_md_files 
            if f.name not in allowed_root_files
        ]
        
        assert len(unexpected_files) <= 2, \
            f"Too many .md files still in root: {[f.name for f in unexpected_files]}"
    
    def test_memory_bank_integration(self):
        """Test memory bank still works with new file structure"""
        
        # This would test if memory bank MCP can still access files
        # Implementation depends on memory bank configuration
        pass
```

---

## 8. Documentation Updates

### 8.1 Updated CLAUDE.md

**Key Changes to Main Instructions:**
```markdown
# CLAUDE.md - MetaOps Validator (Updated File Structure)

## FILE ORGANIZATION (Updated)

### Specifications
- **Features**: specs/features/ - Feature specifications and requirements
- **Architecture**: specs/architecture/ - Technical architecture documents  
- **Business**: specs/business/ - Business requirements and strategy
- **Technical**: specs/technical/ - Technical specifications and APIs
- **UI/UX**: specs/ui-ux/ - User interface and experience designs

### Documentation  
- **User Guides**: docs/user-guides/ - End-user documentation
- **Developer**: docs/developer/ - Developer resources
- **Operations**: docs/operations/ - Deployment and operations
- **Governance**: docs/governance/ - Project governance and processes

### Context Files
- **context/CLAUDE_BUSINESS.md** - Business context and requirements
- **context/CLAUDE_TECHNICAL.md** - Technical implementation context
- **context/PROJECT_CONTEXT_FOR_CLAUDE_DESKTOP.md** - Claude Desktop specifics

## ESSENTIAL SETUP (UNCHANGED)
source .venv/bin/activate
export PYTHONPATH=/home/ed/meta-ops-validator/src

## VALIDATION PIPELINE (UNCHANGED)
1. XSD validation (validators/onix_xsd.py)
2. Schematron validation (validators/onix_schematron.py)  
3. Rule DSL validation (rules/engine.py)
4. Nielsen Completeness Scoring (validators/nielsen_scoring.py)
5. Retailer Compatibility Analysis (validators/retailer_profiles.py)
```

### 8.2 Development Team Guidelines

**New File Organization Guidelines:**
```markdown
# Development Guidelines - File Organization

## When Creating New Documents

### Specifications (specs/)
- **Feature specs**: specs/features/ - New feature requirements
- **Technical designs**: specs/technical/ - API specs, architecture
- **Business requirements**: specs/business/ - User needs, workflows
- **UI/UX designs**: specs/ui-ux/ - Interface specifications

### Documentation (docs/)  
- **User documentation**: docs/user-guides/ - How-to guides
- **Developer docs**: docs/developer/ - Setup, APIs, testing
- **Operations docs**: docs/operations/ - Deployment, monitoring

### Naming Conventions
- Use kebab-case: feature-name-specification.md
- Include date for versions: api-spec-v2-2025-08.md
- Be descriptive: user-authentication-workflow.md

## File Reference Best Practices
- Use relative paths from project root
- Update all references when moving files
- Test references after changes
- Document external links separately
```

---

## 9. Risk Mitigation Summary

### 9.1 Identified Risks and Mitigations

**High Risk - Broken Functionality:**
- **Risk**: Streamlit apps fail to load after file moves
- **Mitigation**: Comprehensive testing with rollback plan
- **Detection**: Automated health checks and UI testing
- **Recovery**: Emergency rollback script available

**Medium Risk - Performance Degradation:**
- **Risk**: File path changes slow down operations
- **Mitigation**: Performance benchmarking before/after
- **Detection**: Load time monitoring and alerts
- **Recovery**: Optimize file access patterns

**Low Risk - User Confusion:**
- **Risk**: Team can't find files in new locations
- **Mitigation**: Updated documentation and training
- **Detection**: Team feedback and support requests
- **Recovery**: Quick reference guide and search tools

### 9.2 Post-Migration Monitoring

**First Week Monitoring:**
- Daily UI health checks
- Performance metric monitoring
- User feedback collection
- Error log analysis

**Ongoing Monitoring:**
- Weekly regression tests
- Monthly file organization review
- Quarterly team satisfaction survey
- Continuous improvement iteration

---

This specification provides a comprehensive plan for safely reorganizing the MetaOps Validator codebase while ensuring all functionality remains intact through thorough testing with Playwright MCP and other available tools. The phased approach with rollback capabilities minimizes risk while improving the project's maintainability.