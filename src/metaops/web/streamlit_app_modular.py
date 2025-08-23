"""
MetaOps Validator Web Interface - Modular Version
Clean, maintainable Streamlit interface for ONIX validation and scoring
"""

import streamlit as st
from typing import Dict, Any

# Import modular components
from metaops.web.components.ui_components import (
    render_custom_css,
    render_file_uploader,
    render_validation_options,
    render_validation_results_table,
    render_nielsen_score_breakdown,
    render_retailer_analysis,
    render_metric_card
)
from metaops.web.components.validation_engine import (
    ValidationRunner,
    display_pipeline_summary,
    display_quick_fix_suggestions
)

# Page config
st.set_page_config(
    page_title="MetaOps Validator",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

def main():
    """Main application entry point."""
    # Apply custom CSS
    render_custom_css()

    # Header
    st.title("📚 MetaOps Validator")
    st.markdown("**Enterprise ONIX validation and metadata completeness scoring**")

    # Sidebar navigation
    page = st.sidebar.selectbox(
        "Navigation",
        ["Single File Validation", "Batch Processing", "Help & Documentation"]
    )

    if page == "Single File Validation":
        render_single_file_page()
    elif page == "Batch Processing":
        render_batch_processing_page()
    elif page == "Help & Documentation":
        render_help_page()


def render_single_file_page():
    """Render the single file validation page."""
    st.header("Single File Validation")

    # File upload
    uploaded_file = render_file_uploader()

    if not uploaded_file:
        render_getting_started_guide()
        return

    # Validation options
    options = render_validation_options()

    # Validate button
    if st.button("🚀 Run Validation Pipeline", type="primary"):
        run_validation_and_display_results(uploaded_file, options)


def render_batch_processing_page():
    """Render the batch processing page."""
    st.header("Batch Processing")
    st.info("Batch processing functionality coming soon. Currently supports single file validation.")

    # Placeholder for batch processing UI
    st.subheader("Upload Multiple Files")
    st.file_uploader("Choose ONIX files", accept_multiple_files=True, type=["xml"])

    st.subheader("Processing Options")
    st.checkbox("Generate comparative report")
    st.checkbox("Export results to CSV")
    st.checkbox("Email results summary")


def render_help_page():
    """Render the help and documentation page."""
    st.header("Help & Documentation")

    # Quick reference
    with st.expander("🔍 Quick Reference", expanded=True):
        st.markdown("""
        ### Validation Stages

        1. **XSD Schema Validation** - Validates XML structure against ONIX 3.0 schema
        2. **Schematron Rules** - Checks publishing industry best practices
        3. **Custom Rules** - Applies publisher-specific validation rules
        4. **Nielsen Scoring** - Analyzes metadata completeness for sales impact
        5. **Retailer Analysis** - Checks compatibility with major retailers

        ### Score Interpretation

        - **90-100%**: Excellent - Maximum sales potential
        - **80-89%**: Good - Strong discoverability
        - **60-79%**: Fair - Moderate sales impact
        - **40-59%**: Poor - Limited discoverability
        - **0-39%**: Critical - Significant sales risk
        """)

    # ONIX basics
    with st.expander("📖 ONIX Basics"):
        st.markdown("""
        ### What is ONIX?

        ONIX (ONline Information eXchange) is the international standard for representing and communicating book industry product information in electronic form.

        ### Supported Formats

        - **ONIX 3.0 Reference Tags** - Uses descriptive XML element names
        - **ONIX 3.0 Short Tags** - Uses numeric codes for smaller file sizes
        - **Namespaced Files** - Include proper XML namespaces (recommended)

        ### Common Issues

        - Missing required fields (ISBN, title, contributors)
        - Incorrect product form codes
        - Missing or incomplete descriptions
        - Territory restrictions not specified
        """)

    # Troubleshooting
    with st.expander("🔧 Troubleshooting"):
        st.markdown("""
        ### Common Problems

        **"No namespace detected"**
        - Your file may be using a toy/demo format
        - Add proper ONIX namespace: `http://ns.editeur.org/onix/3.0/reference`

        **"Schema validation failed"**
        - Check XML structure is valid
        - Ensure required elements are present
        - Verify element nesting follows ONIX standards

        **"Low Nielsen score"**
        - Add missing high-impact fields (description, subjects, series)
        - Improve existing field quality (longer descriptions)
        - Include cover image links
        """)


def render_getting_started_guide():
    """Render getting started guide for new users."""
    st.subheader("Getting Started")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        ### 📁 Upload Your ONIX File

        1. Click "Browse files" above
        2. Select your ONIX XML file (max 50MB)
        3. Choose validation options in the sidebar
        4. Click "Run Validation Pipeline"
        """)

    with col2:
        st.markdown("""
        ### 🎯 What You'll Get

        - **Validation Results** - Detailed error/warning reports
        - **Nielsen Score** - Metadata completeness analysis
        - **Retailer Compatibility** - Platform-specific insights
        - **Quick Fixes** - Actionable improvement suggestions
        """)

    # Sample files info
    st.info("💡 **Need test files?** The system includes generated ONIX samples with varying completeness levels for testing.")


def run_validation_and_display_results(uploaded_file, options: Dict[str, Any]):
    """Run validation pipeline and display results."""
    # Initialize validation runner
    runner = ValidationRunner()

    # Show file info
    st.success(f"✅ Uploaded: **{uploaded_file.name}** ({len(uploaded_file.getvalue()):,} bytes)")

    # Run validation pipeline
    results = runner.run_validation_pipeline(uploaded_file, options)

    # Display pipeline summary
    display_pipeline_summary(results)

    # Display validation status summary
    status_summary = runner.get_validation_status_summary(results)
    if status_summary:
        st.subheader("📋 Status Summary")
        for stage, status in status_summary.items():
            st.markdown(f"**{stage}**: {status}")

    # Create tabs for different result types
    tabs = []
    tab_contents = []

    # XSD Results
    if results.get("xsd_results"):
        tabs.append("🔍 XSD Validation")
        tab_contents.append(("xsd", results["xsd_results"]))

    # Schematron Results
    if results.get("schematron_results"):
        tabs.append("📋 Schematron Rules")
        tab_contents.append(("schematron", results["schematron_results"]))

    # Rules Results
    if results.get("rules_results"):
        tabs.append("⚙️ Custom Rules")
        tab_contents.append(("rules", results["rules_results"]))

    # Nielsen Analysis
    if results.get("nielsen_data") and not results["nielsen_data"].get("error"):
        tabs.append("📊 Nielsen Analysis")
        tab_contents.append(("nielsen", results["nielsen_data"]))

    # Retailer Analysis
    if results.get("retailer_data") and not results["retailer_data"].get("error"):
        tabs.append("🏪 Retailer Analysis")
        tab_contents.append(("retailer", results["retailer_data"]))

    # Quick Fixes
    tabs.append("💡 Quick Fixes")
    tab_contents.append(("fixes", results))

    # Display tabs
    if tabs:
        tab_objects = st.tabs(tabs)

        for i, (tab_type, data) in enumerate(tab_contents):
            with tab_objects[i]:
                if tab_type == "nielsen":
                    render_nielsen_score_breakdown(data)
                elif tab_type == "retailer":
                    render_retailer_analysis(data)
                elif tab_type == "fixes":
                    display_quick_fix_suggestions(data)
                else:
                    # Validation results
                    render_validation_results_table(data, tabs[i])


if __name__ == "__main__":
    main()
