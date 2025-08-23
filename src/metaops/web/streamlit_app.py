"""
MetaOps Validator Web Interface
Basic Streamlit interface for ONIX validation and scoring
"""

import streamlit as st
import pandas as pd
import tempfile
from pathlib import Path
import json
from typing import Dict, Any, List

# Import validation functions
from metaops.validators.onix_xsd import validate_xsd
from metaops.validators.onix_schematron import validate_schematron
from metaops.validators.nielsen_scoring import calculate_nielsen_score
from metaops.validators.retailer_profiles import calculate_retailer_score, calculate_multi_retailer_score, RETAILER_PROFILES
from metaops.rules.engine import evaluate as eval_rules

# Page config
st.set_page_config(
    page_title="MetaOps Validator",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for minimal styling
st.markdown("""
<style>
    .metric-card {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #e9ecef;
    }
    .error-row {
        background: #f8d7da;
        padding: 0.5rem;
        border-radius: 0.25rem;
        margin: 0.25rem 0;
    }
    .warning-row {
        background: #fff3cd;
        padding: 0.5rem;
        border-radius: 0.25rem;
        margin: 0.25rem 0;
    }
    .info-row {
        background: #d1ecf1;
        padding: 0.5rem;
        border-radius: 0.25rem;
        margin: 0.25rem 0;
    }
</style>
""", unsafe_allow_html=True)

def run_full_validation(file_path: Path) -> Dict[str, Any]:
    """Run the complete validation pipeline on an uploaded file."""

    # Initialize results
    results = {
        'xsd_results': [],
        'schematron_results': [],
        'rules_results': [],
        'nielsen_score': None,
        'retailer_analysis': None,
        'pipeline_summary': {
            'total_errors': 0,
            'total_warnings': 0,
            'total_info': 0,
            'stages_completed': []
        }
    }

    try:
        # XSD Validation
        with st.spinner("Running XSD validation..."):
            results['xsd_results'] = validate_xsd(file_path)
            results['pipeline_summary']['stages_completed'].append('XSD')

        # Schematron Validation
        with st.spinner("Running Schematron validation..."):
            results['schematron_results'] = validate_schematron(file_path)
            results['pipeline_summary']['stages_completed'].append('Schematron')

        # Rules Validation
        with st.spinner("Running custom rules..."):
            results['rules_results'] = eval_rules(file_path)
            results['pipeline_summary']['stages_completed'].append('Rules')

        # Nielsen Scoring
        with st.spinner("Calculating Nielsen completeness score..."):
            results['nielsen_score'] = calculate_nielsen_score(file_path)
            results['pipeline_summary']['stages_completed'].append('Nielsen Scoring')

        # Retailer Analysis
        with st.spinner("Analyzing retailer compatibility..."):
            results['retailer_analysis'] = calculate_multi_retailer_score(
                file_path, ['amazon', 'ingram', 'apple', 'kobo']
            )
            results['pipeline_summary']['stages_completed'].append('Retailer Analysis')

        # Count totals
        all_findings = results['xsd_results'] + results['schematron_results'] + results['rules_results']
        results['pipeline_summary']['total_errors'] = len([f for f in all_findings if f.get('level') == 'ERROR'])
        results['pipeline_summary']['total_warnings'] = len([f for f in all_findings if f.get('level') == 'WARNING'])
        results['pipeline_summary']['total_info'] = len([f for f in all_findings if f.get('level') == 'INFO'])

        return results

    except Exception as e:
        st.error(f"Validation failed: {str(e)}")
        return results

def display_nielsen_score(nielsen_data: Dict):
    """Display Nielsen completeness scoring results."""

    st.subheader("📊 Nielsen Completeness Score", help="Metadata completeness scoring based on research correlating quality with sales performance")

    # Main score
    score = nielsen_data['overall_score']
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Overall Score",
            f"{score}%",
            delta=f"{score - 50:.1f}% vs baseline",
            help="Weighted completeness score. 50% is baseline, 75%+ is target for maximum sales impact"
        )

    with col2:
        color = "🟢" if score >= 75 else "🟡" if score >= 50 else "🔴"
        status_text = 'Excellent' if score >= 75 else 'Good' if score >= 50 else 'Needs Work'
        st.metric(
            "Status",
            f"{color} {status_text}",
            help="Quality assessment: Excellent (75%+) = maximum sales potential, Good (50-74%) = solid foundation, Needs Work (<50%) = significant gaps"
        )

    with col3:
        st.metric(
            "Fields Scored",
            f"{nielsen_data['total_score']}/{nielsen_data['total_possible']}",
            help="Weighted points earned vs total possible. Higher weights assigned to fields with greater sales impact"
        )

    # Sales impact
    st.info(f"**Sales Impact Estimate:** {nielsen_data['sales_impact_estimate']}", icon="💰")

    # Field breakdown with tooltips
    st.write("**Field Breakdown:**")

    # Create enhanced breakdown with tooltips
    breakdown_data = []
    field_tooltips = {
        'isbn': 'Unique product identifier - critical for discovery and sales tracking',
        'title': 'Product title - primary discovery mechanism across all channels',
        'contributors': 'Author/editor information - essential for reader identification and browsing',
        'description': 'Product description - key factor in purchase decisions and SEO',
        'subject_codes': 'BISAC/BIC subject classification - drives category placement and discovery',
        'product_form': 'Physical format specification (book, ebook, audio) - affects distribution and pricing',
        'price': 'Retail price information - required for buy button functionality',
        'publication_date': 'Release date - impacts marketing, availability, and catalog organization',
        'publisher': 'Publishing company - affects distribution relationships and brand recognition',
        'imprint': 'Publishing imprint - additional brand/category information for specialized markets',
        'series': 'Series information - drives discoverability for multi-book collections',
        'cover_image': 'Product cover art - significantly impacts conversion rates in online retail'
    }

    for field, score in nielsen_data['breakdown'].items():
        status = "✅" if score > 0 else "❌"
        field_name = field.replace('_', ' ').title()
        tooltip = field_tooltips.get(field, f'{field_name} metadata field')

        breakdown_data.append({
            'Field': field_name,
            'Status': status,
            'Score': score,
            'Impact': tooltip
        })

    df = pd.DataFrame(breakdown_data)

    # Display with expandable details
    with st.expander("📋 View Field Details", expanded=False):
        st.dataframe(df, use_container_width=True, hide_index=True)
        st.caption("💡 Higher scores indicate fields present with quality content. Missing fields (❌) represent opportunity for sales improvement.")

    # Quick summary table
    present_fields = [field.replace('_', ' ').title() for field, score in nielsen_data['breakdown'].items() if score > 0]
    missing_fields = [field.replace('_', ' ').title() for field, score in nielsen_data['breakdown'].items() if score == 0]

    col1, col2 = st.columns(2)
    with col1:
        st.success(f"**Present ({len(present_fields)}):** {', '.join(present_fields[:4])}" + ("..." if len(present_fields) > 4 else ""))
    with col2:
        if missing_fields:
            st.error(f"**Missing ({len(missing_fields)}):** {', '.join(missing_fields[:4])}" + ("..." if len(missing_fields) > 4 else ""))

    # Recommendations
    if nielsen_data.get('missing_critical'):
        st.warning(
            f"**Priority Actions:** Add {', '.join(nielsen_data['missing_critical'][:3])} for immediate impact",
            icon="⚠️"
        )

    st.info(f"**Next Steps:** {nielsen_data.get('recommendation', 'No specific recommendations')}", icon="💡")

def display_retailer_analysis(retailer_data: Dict):
    """Display multi-retailer analysis results."""

    st.subheader("🏪 Retailer Compatibility Analysis", help="Platform-specific metadata requirements analysis for major book retailers")

    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Average Score",
            f"{retailer_data.get('average_score', 0)}%",
            help="Cross-retailer compatibility average. Higher scores indicate better acceptance likelihood across platforms"
        )

    with col2:
        st.metric(
            "Retailers Analyzed",
            retailer_data.get('retailers_analyzed', 0),
            help="Number of retailer profiles evaluated. Each has unique metadata requirements and weighting systems"
        )

    with col3:
        best_retailer = retailer_data.get('best_fit_retailer', 'N/A')
        best_score = retailer_data.get('best_fit_score', 0)
        st.metric(
            "Best Fit",
            f"{best_retailer.title()} ({best_score}%)",
            help="Retailer with highest compatibility score. Consider prioritizing this platform for distribution"
        )

    with col4:
        worst_retailer = retailer_data.get('worst_fit_retailer', 'N/A')
        worst_score = retailer_data.get('worst_fit_score', 0)
        st.metric(
            "Needs Work",
            f"{worst_retailer.title()} ({worst_score}%)",
            help="Retailer requiring most metadata improvements. Focus enhancement efforts here"
        )

    # Common gaps with explanation
    if retailer_data.get('common_gaps'):
        st.warning(
            f"**Cross-Platform Issues:** {', '.join(retailer_data['common_gaps'][:5])}",
            icon="⚠️"
        )
        st.caption("💡 These fields are missing across multiple retailers - fixing them provides maximum impact")

    # Recommendation
    st.info(f"**Strategic Focus:** {retailer_data.get('recommendation', 'Continue with current metadata approach')}", icon="🎯")

    # Detailed retailer breakdown with enhanced tooltips
    if retailer_data.get('retailer_details'):
        st.write("**Platform-Specific Analysis:**")

        retailer_breakdown = []
        retailer_explanations = {
            'amazon': 'World\'s largest book retailer - prioritizes rich descriptions and subject codes for search',
            'ingram': 'Major book distributor - requires publisher info and complete bibliographic data',
            'apple': 'Premium digital platform - emphasizes quality descriptions and editorial content',
            'kobo': 'Global ebook platform - focuses on discoverability and series information',
            'barnes_noble': 'Major US retailer - balances traditional and digital requirements',
            'overdrive': 'Library platform - prioritizes cataloging data and institutional metadata'
        }

        for retailer_key, details in retailer_data['retailer_details'].items():
            if isinstance(details, dict) and 'overall_score' in details:
                risk_color = "🟢" if details.get('risk_level') == 'LOW' else "🟡" if details.get('risk_level') == 'MEDIUM' else "🔴"
                compliance_color = "✅" if details.get('compliance_status') == 'COMPLIANT' else "⚠️" if details.get('compliance_status') == 'PARTIAL_COMPLIANCE' else "❌"

                retailer_breakdown.append({
                    'Platform': details.get('retailer', retailer_key),
                    'Score': f"{details['overall_score']}%",
                    'Risk': f"{risk_color} {details.get('risk_level', 'Unknown')}",
                    'Status': f"{compliance_color} {details.get('compliance_status', 'Unknown').replace('_', ' ').title()}",
                    'Missing': len(details.get('critical_missing', [])),
                    'Focus': retailer_explanations.get(retailer_key, 'Platform-specific requirements')
                })

        if retailer_breakdown:
            df = pd.DataFrame(retailer_breakdown)
            st.dataframe(df, use_container_width=True, hide_index=True)

            # Detailed retailer insights
            with st.expander("🔍 Platform-Specific Insights", expanded=False):
                for retailer_key, details in retailer_data['retailer_details'].items():
                    if isinstance(details, dict) and 'recommendations' in details:
                        retailer_name = details.get('retailer', retailer_key)
                        st.write(f"**{retailer_name}**")

                        col1, col2 = st.columns(2)
                        with col1:
                            st.write(f"• Score: {details['overall_score']}%")
                            st.write(f"• Risk Level: {details.get('risk_level', 'Unknown')}")
                            if details.get('critical_missing'):
                                st.write(f"• Missing: {', '.join(details['critical_missing'][:3])}")

                        with col2:
                            if details.get('recommendations'):
                                st.write(f"• Action: {details['recommendations'][0][:60]}...")
                            discovery_score = details.get('discovery_score', 0)
                            st.write(f"• Discovery Score: {discovery_score}%")

                        st.divider()

def display_validation_findings(findings: List[Dict], title: str):
    """Display validation findings in a structured format."""

    # Define tooltips for validation stages
    validation_tooltips = {
        'XSD Schema Validation': 'Structural validation against ONIX 3.0 XML Schema Definition. Ensures proper XML structure and required elements.',
        'Schematron Business Rules': 'Business logic validation using Schematron patterns. Checks relationships, constraints, and publishing industry rules.',
        'Custom Rules Engine': 'Publisher-specific validation rules. Includes contract compliance, territory restrictions, and custom business logic.'
    }

    tooltip_text = validation_tooltips.get(title, f'{title} validation results')

    if not findings:
        st.success(f"✅ {title}: No issues found", icon="✅")
        st.caption(f"💡 {tooltip_text}")
        return

    st.subheader(f"⚠️ {title}", help=tooltip_text)

    # Count by severity
    errors = [f for f in findings if f.get('level') == 'ERROR']
    warnings = [f for f in findings if f.get('level') in ['WARNING', 'WARN']]
    infos = [f for f in findings if f.get('level') == 'INFO']

    # Summary with tooltips
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(
            "Errors",
            len(errors),
            help="Critical issues that prevent processing or distribution. Must be fixed."
        )
    with col2:
        st.metric(
            "Warnings",
            len(warnings),
            help="Potential issues that may affect quality or compatibility. Should be reviewed."
        )
    with col3:
        st.metric(
            "Info",
            len(infos),
            help="Informational messages and successful validation confirmations."
        )

    # Enhanced findings display with explanations
    if len(findings) > 5:
        with st.expander(f"📋 Show All {len(findings)} Findings", expanded=False):
            _display_findings_list(findings)
    else:
        _display_findings_list(findings)

    # Quick fix suggestions for common issues
    _show_quick_fixes(findings)

def _display_findings_list(findings: List[Dict]):
    """Display individual findings with enhanced formatting."""
    for i, finding in enumerate(findings):
        level = finding.get('level', 'INFO')
        message = finding.get('message', 'No message')
        line = finding.get('line', 'N/A')
        domain = finding.get('domain', 'UNKNOWN')

        # Create enhanced message with context
        enhanced_message = f"**Line {line}:** {message}"

        # Add technical details if available
        details = []
        if finding.get('rule_id'):
            details.append(f"Rule: {finding['rule_id']}")
        if finding.get('domain') and finding['domain'] != 'UNKNOWN':
            details.append(f"Domain: {finding['domain']}")
        if finding.get('namespace'):
            details.append(f"Namespace: {'ONIX 3.0' if 'onix' in finding['namespace'] else 'Other'}")

        if details:
            enhanced_message += f"\n*{' | '.join(details)}*"

        # Add explanation if available
        if finding.get('explanation'):
            enhanced_message += f"\n💡 {finding['explanation']}"

        # Display with appropriate styling
        if level == 'ERROR':
            st.error(enhanced_message, icon="🚫")
        elif level in ['WARNING', 'WARN']:
            st.warning(enhanced_message, icon="⚠️")
        else:
            st.info(enhanced_message, icon="ℹ️")

def _show_quick_fixes(findings: List[Dict]):
    """Show quick fix suggestions for common validation issues."""
    error_patterns = {}
    for finding in findings:
        if finding.get('level') == 'ERROR':
            message = finding.get('message', '').lower()
            if 'isbn' in message:
                error_patterns['isbn'] = "ISBN format issues detected"
            elif 'missing child' in message or 'required' in message:
                error_patterns['structure'] = "Required elements missing"
            elif 'namespace' in message:
                error_patterns['namespace'] = "Namespace declaration issues"
            elif 'unexpected' in message or 'not expected' in message:
                error_patterns['order'] = "Element ordering or structure issues"

    if error_patterns:
        st.subheader("🔧 Quick Fix Suggestions")

        quick_fixes = {
            'isbn': "Ensure ISBN-13 format (13 digits) and use ProductIDType '15' for ISBN-13 or '03' for ISBN-10",
            'structure': "Review ONIX 3.0 schema requirements and ensure all mandatory child elements are present",
            'namespace': "Add proper ONIX namespace declaration: xmlns='http://ns.editeur.org/onix/3.0/reference'",
            'order': "Check element ordering against ONIX schema - elements must appear in correct sequence"
        }

        for pattern, fix in quick_fixes.items():
            if pattern in error_patterns:
                st.info(f"**{error_patterns[pattern]}:** {fix}", icon="🔧")

def main():
    """Main Streamlit application."""

    # Header
    st.title("📚 MetaOps Validator")
    st.markdown("*Pre-feed ONIX validation and metadata completeness scoring*")

    # Sidebar
    st.sidebar.header("🔧 Configuration Options")

    # File upload
    uploaded_file = st.sidebar.file_uploader(
        "Upload ONIX XML File",
        type=['xml'],
        accept_multiple_files=False,
        help="Upload an ONIX 3.0 XML file for comprehensive validation and scoring. Supports both reference and short-tag variants."
    )

    # Validation options with detailed tooltips
    st.sidebar.subheader("Pipeline Stages", help="Select which validation and analysis stages to execute. Each stage provides different insights.")

    run_xsd = st.sidebar.checkbox(
        "XSD Schema Validation",
        value=True,
        help="Validates XML structure against official ONIX 3.0 schema definitions. Ensures proper element hierarchy and data types."
    )

    run_schematron = st.sidebar.checkbox(
        "Schematron Business Rules",
        value=True,
        help="Applies business logic validation using Schematron patterns. Checks publishing industry best practices and relationships."
    )

    run_rules = st.sidebar.checkbox(
        "Custom Rule Engine",
        value=True,
        help="Executes publisher-specific validation rules including contract compliance and territory restrictions."
    )

    run_nielsen = st.sidebar.checkbox(
        "Nielsen Completeness Scoring",
        value=True,
        help="Calculates metadata completeness score based on research correlating quality with sales performance (up to 75% uplift)."
    )

    run_retailer = st.sidebar.checkbox(
        "Retailer Compatibility Analysis",
        value=True,
        help="Analyzes metadata against platform-specific requirements for Amazon, IngramSpark, Apple Books, and other major retailers."
    )

    # Main content
    if not uploaded_file:
        # Welcome screen
        st.markdown("""
        ## Welcome to MetaOps Validator

        This tool provides comprehensive ONIX metadata validation and scoring:

        ### 🔍 **Validation Pipeline**
        - **XSD Schema:** Structural validation against ONIX 3.0 standards
        - **Schematron Rules:** Business logic and relationship validation
        - **Custom Rules:** Publisher-specific requirements

        ### 📊 **Completeness Scoring**
        - **Nielsen Analysis:** Metadata completeness correlation with sales performance
        - **Retailer Profiles:** Platform-specific requirement analysis

        ### 🚀 **Getting Started**
        1. Upload an ONIX XML file using the sidebar
        2. Select validation stages to run
        3. Review results and recommendations

        ---
        *Upload a file to begin validation*
        """)

        # Sample results teaser
        with st.expander("📋 Sample Results Preview"):
            st.image("data:image/svg+xml,%3Csvg width='400' height='200' xmlns='http://www.w3.org/2000/svg'%3E%3Crect width='100%25' height='100%25' fill='%23f8f9fa'/%3E%3Ctext x='50%25' y='50%25' font-size='18' text-anchor='middle' dy='.3em' fill='%23666'%3EValidation Results Dashboard%3C/text%3E%3C/svg%3E",
                     caption="Results will appear here after validation")

        return

    # Process uploaded file
    st.markdown("---")
    st.header(f"🔍 Validating: {uploaded_file.name}")

    # Save uploaded file temporarily
    with tempfile.NamedTemporaryFile(suffix='.xml', delete=False) as tmp_file:
        tmp_file.write(uploaded_file.getvalue())
        tmp_file.flush()
        temp_path = Path(tmp_file.name)

    try:
        # Run validation
        results = run_full_validation(temp_path)

        # Pipeline summary
        st.success(f"✅ Validation Complete: {len(results['pipeline_summary']['stages_completed'])} stages processed")

        # Display results in tabs
        tab1, tab2, tab3, tab4 = st.tabs(["📊 Scoring", "⚠️ Validation Issues", "🔧 Technical Details", "📋 Raw Data"])

        with tab1:
            # Nielsen scoring
            if run_nielsen and results['nielsen_score']:
                display_nielsen_score(results['nielsen_score'])
                st.markdown("---")

            # Retailer analysis
            if run_retailer and results['retailer_analysis']:
                display_retailer_analysis(results['retailer_analysis'])

        with tab2:
            # Validation findings
            if run_xsd and results['xsd_results']:
                display_validation_findings(results['xsd_results'], "XSD Schema Validation")
                st.markdown("---")

            if run_schematron and results['schematron_results']:
                display_validation_findings(results['schematron_results'], "Schematron Business Rules")
                st.markdown("---")

            if run_rules and results['rules_results']:
                display_validation_findings(results['rules_results'], "Custom Rules Engine")

        with tab3:
            # Technical summary
            st.subheader("🔧 Pipeline Summary")
            summary = results['pipeline_summary']

            col1, col2 = st.columns(2)
            with col1:
                st.metric("Stages Completed", len(summary['stages_completed']))
                st.write("**Stages:** " + " → ".join(summary['stages_completed']))

            with col2:
                st.metric("Total Issues", summary['total_errors'] + summary['total_warnings'])
                st.write(f"**Breakdown:** {summary['total_errors']} errors, {summary['total_warnings']} warnings, {summary['total_info']} info")

        with tab4:
            # Raw JSON data
            st.subheader("📋 Raw Validation Data")
            st.json({
                'nielsen_score': results['nielsen_score'],
                'retailer_analysis': results['retailer_analysis'],
                'validation_findings': len(results['xsd_results'] + results['schematron_results'] + results['rules_results']),
                'pipeline_summary': results['pipeline_summary']
            })

    finally:
        # Cleanup temporary file
        if temp_path.exists():
            temp_path.unlink()

if __name__ == "__main__":
    main()
