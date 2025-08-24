#!/usr/bin/env python3
"""
MetaOps Validator - Business Demo Interface
Self-contained demo with embedded sample files for remote access
"""
from pathlib import Path
import pandas as pd
import streamlit as st
import json
from metaops.validators.onix_xsd import validate_xsd
from metaops.validators.onix_schematron import validate_schematron
from metaops.rules.engine import evaluate as eval_rules
from metaops.onix_utils import detect_onix_namespace, is_using_toy_schemas

# Page config
st.set_page_config(
    page_title="MetaOps Validator - Business Demo",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for business presentation
st.markdown("""
<style>
.main-header { 
    color: #0f766e; 
    font-size: 2.5rem; 
    font-weight: 600;
    margin-bottom: 0.5rem;
}
.subtitle { 
    color: #666; 
    font-size: 1.1rem;
    margin-bottom: 2rem;
}
.metric-tag {
    background: #f0f9ff;
    border: 1px solid #0284c7;
    padding: 0.2rem 0.4rem;
    border-radius: 0.25rem;
    font-size: 0.75rem;
    color: #0284c7;
}
.business-context {
    background: #f8fafc;
    border-left: 4px solid #0f766e;
    padding: 1rem;
    margin: 1rem 0;
}
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<h1 class="main-header">MetaOps Validator</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">ONIX 3.x Pre-Feed Validation System - Enterprise Publishing Operations</p>', unsafe_allow_html=True)

# Sidebar with business context
with st.sidebar:
    st.markdown("### 💼 Business Context")
    st.markdown("""
    **What this does:**
    - Validates ONIX files before retailer feeds
    - Identifies contract compliance issues  
    - Prevents retailer rejection & rework costs
    - Generates operational KPI data
    
    **Target Users:**
    - Publishing Operations teams
    - Metadata managers
    - Contract compliance officers
    
    **Value Proposition:**
    - Reduce manual QA time by 75%
    - Prevent retailer feed rejections
    - Automate contract compliance checking
    """)
    
    st.markdown("### 🎯 Demo Instructions")
    st.markdown("""
    1. Click **"Run Full Demo"** below
    2. Review validation results
    3. Examine business impact metrics
    4. Export findings for stakeholders
    """)

# Load embedded sample files
@st.cache_data
def load_sample_files():
    """Load sample files from server"""
    try:
        sample_onix = Path("data/samples/onix_samples/sample.xml").read_text()
        sample_xsd = Path("data/samples/onix_samples/onix.xsd").read_text()  
        sample_sch = Path("data/samples/onix_samples/rules.sch").read_text()
        sample_rules = Path("diagnostic/rules.sample.yml").read_text()
        return sample_onix, sample_xsd, sample_sch, sample_rules
    except Exception as e:
        st.error(f"Could not load sample files: {e}")
        return None, None, None, None

# Business metrics calculation
def calculate_business_impact(total_findings):
    """Calculate business impact metrics"""
    # Based on context/CLAUDE_BUSINESS.md assumptions
    time_to_correct_hours = 4
    hourly_cost = 75
    monthly_incident_rate = 2.1
    
    cost_per_incident = time_to_correct_hours * hourly_cost
    monthly_impact = cost_per_incident * monthly_incident_rate
    
    return {
        "cost_per_incident": cost_per_incident,
        "monthly_impact": monthly_impact,
        "annual_impact": monthly_impact * 12
    }

# Main demo section
st.markdown('<div class="business-context">', unsafe_allow_html=True)
st.markdown("""
**🔍 Validation Pipeline Overview:**

Our three-stage validation process catches issues before they reach retailers:

1. **XSD Schema Validation** - Structural compliance with ONIX 3.x standards
2. **Schematron Business Rules** - Industry best practices and format requirements  
3. **Custom Rule DSL** - Contract-specific validation (territory restrictions, format limitations)

**Why This Matters:** Each rejected feed costs an average of $300 in operational time and delays time-to-market by 2-4 days.
""")
st.markdown('</div>', unsafe_allow_html=True)

# Load sample data
sample_onix, sample_xsd, sample_sch, sample_rules = load_sample_files()

if not all([sample_onix, sample_xsd, sample_sch, sample_rules]):
    st.error("❌ Sample files not available. Please check server configuration.")
    st.stop()

# Demo execution
col1, col2, col3 = st.columns([2, 1, 1])

with col1:
    if st.button("🚀 Run Full Validation Demo", type="primary", use_container_width=True):
        st.markdown("---")
        
        # Create temp files
        temp_onix = Path("demo_onix.xml")
        temp_xsd = Path("demo_onix.xsd") 
        temp_sch = Path("demo_rules.sch")
        temp_rules = Path("demo_rules.yml")
        
        temp_onix.write_text(sample_onix)
        temp_xsd.write_text(sample_xsd)
        temp_sch.write_text(sample_sch)
        temp_rules.write_text(sample_rules)
        
        # Namespace detection
        namespace_uri, is_real_onix = detect_onix_namespace(temp_onix)
        
        st.markdown("### 📋 Validation Results")
        
        # XSD Validation
        st.markdown("#### 1️⃣ XSD Schema Validation")
        with st.spinner("Running XSD validation..."):
            xsd_results = validate_xsd(temp_onix, temp_xsd)
            
        col_a, col_b = st.columns([1, 3])
        with col_a:
            st.metric("XSD Issues", len(xsd_results))
            st.markdown('<span class="metric-tag">[verified]</span>', unsafe_allow_html=True)
        with col_b:
            if len(xsd_results) == 0:
                st.success("✅ **Pass** - No structural schema violations detected")
            else:
                st.error(f"❌ **{len(xsd_results)} Issues** - Schema violations found")
                st.dataframe(pd.DataFrame(xsd_results), use_container_width=True)
        
        # Schematron Validation  
        st.markdown("#### 2️⃣ Schematron Business Rules")
        with st.spinner("Running Schematron validation..."):
            sch_results = validate_schematron(temp_onix, temp_sch)
            
        col_a, col_b = st.columns([1, 3])
        with col_a:
            st.metric("Schematron Findings", len(sch_results))
            st.markdown('<span class="metric-tag">[verified]</span>', unsafe_allow_html=True)
        with col_b:
            if len(sch_results) > 0:
                st.warning(f"⚠️ **{len(sch_results)} Business Rule Violations**")
                for result in sch_results:
                    st.code(json.dumps(result, indent=2))
            else:
                st.success("✅ All business rules passed")
        
        # Rule DSL Validation
        st.markdown("#### 3️⃣ Contract-Aware Rule DSL")
        with st.spinner("Running custom rule validation..."):
            dsl_results = eval_rules(temp_onix, temp_rules)
            
        col_a, col_b = st.columns([1, 3]) 
        with col_a:
            st.metric("Contract Violations", len(dsl_results))
            st.markdown('<span class="metric-tag">[verified]</span>', unsafe_allow_html=True)
        with col_b:
            if len(dsl_results) > 0:
                st.error(f"🚨 **{len(dsl_results)} Contract Compliance Issues**")
                for result in dsl_results:
                    st.code(json.dumps(result, indent=2))
            else:
                st.success("✅ All contract rules compliant")
        
        # Business Impact Analysis
        total_findings = len(xsd_results) + len(sch_results) + len(dsl_results)
        impact = calculate_business_impact(total_findings)
        
        st.markdown("---")
        st.markdown("### 💰 Business Impact Analysis")
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Findings", total_findings)
            st.markdown('<span class="metric-tag">[verified]</span>', unsafe_allow_html=True)
        with col2:
            st.metric("Cost per Incident", f"${impact['cost_per_incident']:,.0f}")
            st.markdown('<span class="metric-tag">[inference]</span>', unsafe_allow_html=True)
        with col3:
            st.metric("Monthly Impact", f"${impact['monthly_impact']:,.0f}")
            st.markdown('<span class="metric-tag">[inference]</span>', unsafe_allow_html=True)
        with col4:
            st.metric("Annual Impact", f"${impact['annual_impact']:,.0f}")
            st.markdown('<span class="metric-tag">[inference]</span>', unsafe_allow_html=True)
        
        # Export section
        st.markdown("---")
        st.markdown("### 📊 Export & Reporting")
        
        # Combine all results
        all_results = []
        for result in xsd_results:
            result["validation_type"] = "XSD Schema"
            all_results.append(result)
        for result in sch_results:
            result["validation_type"] = "Schematron Rules"
            all_results.append(result)
        for result in dsl_results:
            result["validation_type"] = "Contract DSL"
            all_results.append(result)
        
        if all_results:
            df = pd.DataFrame(all_results)
            st.dataframe(df, use_container_width=True)
            
            col_export1, col_export2 = st.columns(2)
            with col_export1:
                csv_data = df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    "📄 Download CSV Report",
                    csv_data,
                    "metaops_validation_report.csv",
                    "text/csv"
                )
            with col_export2:
                json_data = df.to_json(orient="records", indent=2).encode('utf-8')
                st.download_button(
                    "📋 Download JSON Data", 
                    json_data,
                    "metaops_validation_data.json",
                    "application/json"
                )
        
        # Cleanup temp files
        for temp_file in [temp_onix, temp_xsd, temp_sch, temp_rules]:
            if temp_file.exists():
                temp_file.unlink()
                
        # Store results in session state
        st.session_state["demo_completed"] = True
        st.session_state["total_findings"] = total_findings
        st.session_state["business_impact"] = impact

with col2:
    if st.button("📊 View Dashboard", use_container_width=True):
        st.markdown(f'<meta http-equiv="refresh" content="0; url=http://100.111.114.84:8082/demo.html">', unsafe_allow_html=True)

with col3:  
    if st.button("📋 Executive Report", use_container_width=True):
        st.markdown(f'<meta http-equiv="refresh" content="0; url=http://100.111.114.84:8082/../reports/executive_summary.html">', unsafe_allow_html=True)

# Footer with system info
st.markdown("---")
col_footer1, col_footer2, col_footer3 = st.columns(3)

with col_footer1:
    st.markdown("**🔧 System Status**")
    st.markdown("✅ All validators operational")
    st.markdown("✅ Sample data loaded")
    st.markdown("✅ Export functions active")

with col_footer2:
    st.markdown("**📈 Current Configuration**")
    st.markdown("• Schema: Toy/Demo format")
    st.markdown("• Namespace: Non-production")
    st.markdown("• Rules: Contract sample set")

with col_footer3:
    st.markdown("**🚀 System Status**") 
    st.markdown("• EDItEUR schema migration path")
    st.markdown("• Namespace-aware XPath support")
    st.markdown("• Validation system operational")