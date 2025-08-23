"""
Reusable UI components for Streamlit web interface.
"""

import streamlit as st
import pandas as pd
from typing import Dict, Any, List, Optional


def render_custom_css():
    """Apply custom CSS styling to the Streamlit app."""
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
        .score-excellent { color: #28a745; font-weight: bold; }
        .score-good { color: #20c997; font-weight: bold; }
        .score-fair { color: #ffc107; font-weight: bold; }
        .score-poor { color: #fd7e14; font-weight: bold; }
        .score-critical { color: #dc3545; font-weight: bold; }
        .tooltip {
            background: #343a40;
            color: white;
            padding: 0.5rem;
            border-radius: 0.25rem;
            font-size: 0.875rem;
            margin-top: 0.25rem;
        }
    </style>
    """, unsafe_allow_html=True)


def render_score_badge(score: float, label: str = "Score") -> str:
    """Render a colored score badge based on score value."""
    if score >= 90:
        css_class = "score-excellent"
        grade = "A+"
    elif score >= 80:
        css_class = "score-good"
        grade = "A"
    elif score >= 70:
        css_class = "score-good"
        grade = "B+"
    elif score >= 60:
        css_class = "score-fair"
        grade = "B"
    elif score >= 50:
        css_class = "score-fair"
        grade = "C"
    else:
        css_class = "score-critical" if score < 30 else "score-poor"
        grade = "F" if score < 30 else "D"

    return f'<span class="{css_class}">{label}: {score:.1f}% ({grade})</span>'


def render_metric_card(title: str, value: str, help_text: Optional[str] = None):
    """Render a metric card with optional tooltip."""
    with st.container():
        st.markdown(f"""
        <div class="metric-card">
            <h4>{title}</h4>
            <p style="font-size: 1.5rem; margin: 0;">{value}</p>
            {f'<div class="tooltip">{help_text}</div>' if help_text else ''}
        </div>
        """, unsafe_allow_html=True)


def render_validation_results_table(results: List[Dict[str, Any]], title: str = "Validation Results"):
    """Render validation results in a formatted table."""
    if not results:
        st.info(f"No {title.lower()} to display.")
        return

    st.subheader(title)

    # Convert to DataFrame for display
    df_data = []
    for result in results:
        df_data.append({
            "Line": result.get("line", 1),
            "Level": result.get("level", "INFO"),
            "Type": result.get("type", "unknown"),
            "Message": result.get("message", "No message"),
            "Domain": result.get("domain", "N/A")
        })

    df = pd.DataFrame(df_data)

    # Style the table based on level
    def style_level(val):
        if val == "ERROR":
            return "background-color: #f8d7da; color: #721c24;"
        elif val == "WARNING":
            return "background-color: #fff3cd; color: #856404;"
        elif val == "INFO":
            return "background-color: #d1ecf1; color: #0c5460;"
        return ""

    styled_df = df.style.applymap(style_level, subset=["Level"])
    st.dataframe(styled_df, use_container_width=True)


def render_nielsen_score_breakdown(nielsen_data: Dict[str, Any]):
    """Render Nielsen completeness score breakdown."""
    if not nielsen_data or nielsen_data.get("error"):
        st.error(f"Nielsen scoring error: {nielsen_data.get('error', 'Unknown error')}")
        return

    overall_score = nielsen_data.get("overall_score", 0)

    st.subheader("📊 Nielsen Completeness Analysis")

    col1, col2, col3 = st.columns([2, 1, 1])

    with col1:
        st.markdown(render_score_badge(overall_score, "Overall Score"), unsafe_allow_html=True)

        sales_impact = nielsen_data.get("sales_impact_estimate", "Unknown")
        st.write(f"**Sales Impact**: {sales_impact}")

        if nielsen_data.get("recommendation"):
            st.write(f"**Recommendation**: {nielsen_data['recommendation']}")

    with col2:
        products_count = nielsen_data.get("products_count", 1)
        st.metric("Products Analyzed", products_count)

        if "min_score" in nielsen_data:
            st.metric("Min Score", f"{nielsen_data['min_score']:.1f}%")

    with col3:
        total_possible = nielsen_data.get("total_possible", 100)
        st.metric("Max Possible", total_possible)

        if "max_score" in nielsen_data:
            st.metric("Max Score", f"{nielsen_data['max_score']:.1f}%")

    # Field breakdown
    if "products_scores" in nielsen_data and nielsen_data["products_scores"]:
        st.subheader("Field Breakdown (First Product)")
        first_product = nielsen_data["products_scores"][0]
        breakdown = first_product.get("breakdown", {})

        if breakdown:
            breakdown_df = pd.DataFrame([
                {"Field": field, "Score": score, "Weight": {"isbn": 20, "title": 15, "contributors": 12, "description": 10, "subject_codes": 8, "product_form": 8, "price": 7, "publication_date": 5, "publisher": 5, "imprint": 4, "series": 3, "cover_image": 3}.get(field, 0)}
                for field, score in breakdown.items()
            ])
            breakdown_df["Percentage"] = (breakdown_df["Score"] / breakdown_df["Weight"] * 100).round(1)
            st.dataframe(breakdown_df, use_container_width=True)


def render_retailer_analysis(retailer_data: Dict[str, Any]):
    """Render retailer compatibility analysis."""
    if not retailer_data or retailer_data.get("error"):
        st.error(f"Retailer analysis error: {retailer_data.get('error', 'Unknown error')}")
        return

    st.subheader("🏪 Multi-Retailer Analysis")

    # Overall metrics
    avg_score = retailer_data.get("average_score", 0)
    best_retailer = retailer_data.get("best_retailer", "N/A")
    worst_retailer = retailer_data.get("worst_retailer", "N/A")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(render_score_badge(avg_score, "Average Score"), unsafe_allow_html=True)

    with col2:
        st.metric("Best Match", best_retailer)

    with col3:
        st.metric("Needs Work", worst_retailer)

    # Individual retailer scores
    retailer_scores = retailer_data.get("retailer_scores", {})
    if retailer_scores:
        st.subheader("Individual Retailer Scores")

        score_data = []
        for retailer, score_info in retailer_scores.items():
            score_data.append({
                "Retailer": score_info.get("retailer", retailer.title()),
                "Score": f"{score_info.get('overall_score', 0):.1f}%",
                "Risk Level": score_info.get("risk_level", "UNKNOWN"),
                "Critical Missing": ", ".join(score_info.get("critical_missing", [])[:3]) + ("..." if len(score_info.get("critical_missing", [])) > 3 else ""),
                "Products": score_info.get("products_count", 1)
            })

        score_df = pd.DataFrame(score_data)
        st.dataframe(score_df, use_container_width=True)


def render_file_uploader(accepted_types: List[str] = None) -> Optional[Any]:
    """Render file uploader with validation."""
    if accepted_types is None:
        accepted_types = ["xml"]

    uploaded_file = st.file_uploader(
        "Choose ONIX XML file",
        type=accepted_types,
        help="Upload an ONIX 3.0 XML file for validation and analysis"
    )

    if uploaded_file:
        # Basic validation
        if not uploaded_file.name.lower().endswith('.xml'):
            st.error("Please upload an XML file.")
            return None

        # Size check (50MB limit)
        if hasattr(uploaded_file, 'size') and uploaded_file.size:
            if uploaded_file.size > 50 * 1024 * 1024:
                st.error("File too large. Maximum size is 50MB.")
                return None

        return uploaded_file

    return None


def render_validation_options():
    """Render validation options in sidebar."""
    st.sidebar.subheader("Validation Options")

    options = {}

    options["run_xsd"] = st.sidebar.checkbox(
        "XSD Schema Validation",
        value=True,
        help="Validate XML structure against ONIX schema"
    )

    options["run_schematron"] = st.sidebar.checkbox(
        "Schematron Business Rules",
        value=True,
        help="Check publishing industry best practices"
    )

    options["run_rules"] = st.sidebar.checkbox(
        "Custom Rule Engine",
        value=True,
        help="Apply publisher-specific validation rules"
    )

    options["run_nielsen"] = st.sidebar.checkbox(
        "Nielsen Completeness Scoring",
        value=True,
        help="Analyze metadata completeness for sales impact"
    )

    options["run_retailer"] = st.sidebar.checkbox(
        "Retailer Compatibility Analysis",
        value=True,
        help="Check compatibility with major book retailers"
    )

    if options["run_retailer"]:
        available_retailers = ["amazon", "ingram", "apple", "kobo", "barnes_noble"]
        options["selected_retailers"] = st.sidebar.multiselect(
            "Select Retailers",
            available_retailers,
            default=["amazon", "ingram", "apple"],
            help="Choose retailers to analyze compatibility"
        )

    return options
