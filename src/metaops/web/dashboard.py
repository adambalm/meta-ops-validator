"""
MetaOps Validator Results Dashboard
Advanced analytics and batch processing interface
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import tempfile
import zipfile
from pathlib import Path
import json
from typing import Dict, List, Any
from datetime import datetime, timedelta
import io

# Import validation functions
from metaops.validators.onix_xsd import validate_xsd
from metaops.validators.onix_schematron import validate_schematron
from metaops.validators.nielsen_scoring import calculate_nielsen_score
from metaops.validators.retailer_profiles import calculate_multi_retailer_score, RETAILER_PROFILES
from metaops.rules.engine import evaluate as eval_rules

st.set_page_config(
    page_title="MetaOps Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for dashboard styling
st.markdown("""
<style>
    .metric-container {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        margin: 0.5rem 0;
    }
    .score-high { border-left: 5px solid #28a745; }
    .score-medium { border-left: 5px solid #ffc107; }
    .score-low { border-left: 5px solid #dc3545; }
    .dashboard-card {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        border: 1px solid #dee2e6;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

def process_batch_files(uploaded_files) -> Dict[str, Any]:
    """Process multiple ONIX files and generate analytics."""
    
    batch_results = {
        'files_processed': 0,
        'total_errors': 0,
        'total_warnings': 0,
        'nielsen_scores': [],
        'retailer_scores': [],
        'file_details': [],
        'processing_summary': {
            'avg_nielsen_score': 0,
            'avg_retailer_score': 0,
            'compliance_rate': 0,
            'common_issues': []
        }
    }
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    all_issues = []
    
    for i, uploaded_file in enumerate(uploaded_files):
        status_text.text(f"Processing {uploaded_file.name}...")
        progress_bar.progress((i + 1) / len(uploaded_files))
        
        # Save file temporarily
        with tempfile.NamedTemporaryFile(suffix='.xml', delete=False) as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            tmp_file.flush()
            temp_path = Path(tmp_file.name)
        
        try:
            # Run validation pipeline
            xsd_results = validate_xsd(temp_path)
            schematron_results = validate_schematron(temp_path)
            rules_results = eval_rules(temp_path)
            nielsen_data = calculate_nielsen_score(temp_path)
            retailer_data = calculate_multi_retailer_score(temp_path, ['amazon', 'ingram', 'apple'])
            
            # Count issues
            all_findings = xsd_results + schematron_results + rules_results
            file_errors = len([f for f in all_findings if f.get('level') == 'ERROR'])
            file_warnings = len([f for f in all_findings if f.get('level') in ['WARNING', 'WARN']])
            
            # Collect data
            batch_results['files_processed'] += 1
            batch_results['total_errors'] += file_errors
            batch_results['total_warnings'] += file_warnings
            batch_results['nielsen_scores'].append(nielsen_data['overall_score'])
            batch_results['retailer_scores'].append(retailer_data.get('average_score', 0))
            
            # Store file details
            batch_results['file_details'].append({
                'filename': uploaded_file.name,
                'nielsen_score': nielsen_data['overall_score'],
                'retailer_score': retailer_data.get('average_score', 0),
                'errors': file_errors,
                'warnings': file_warnings,
                'compliance_status': 'Pass' if file_errors == 0 else 'Fail',
                'missing_critical': len(nielsen_data.get('missing_critical', [])),
                'sales_impact': nielsen_data.get('sales_impact_estimate', 'Unknown'),
                'best_retailer': retailer_data.get('best_fit_retailer', 'N/A'),
                'worst_retailer': retailer_data.get('worst_fit_retailer', 'N/A')
            })
            
            # Collect common issues
            for finding in all_findings:
                if finding.get('level') == 'ERROR':
                    all_issues.append(finding.get('message', 'Unknown error'))
        
        except Exception as e:
            st.error(f"Error processing {uploaded_file.name}: {str(e)}")
        
        finally:
            # Cleanup
            if temp_path.exists():
                temp_path.unlink()
    
    # Calculate summary statistics
    if batch_results['nielsen_scores']:
        batch_results['processing_summary']['avg_nielsen_score'] = sum(batch_results['nielsen_scores']) / len(batch_results['nielsen_scores'])
    
    if batch_results['retailer_scores']:
        batch_results['processing_summary']['avg_retailer_score'] = sum(batch_results['retailer_scores']) / len(batch_results['retailer_scores'])
    
    passing_files = len([f for f in batch_results['file_details'] if f['compliance_status'] == 'Pass'])
    batch_results['processing_summary']['compliance_rate'] = (passing_files / batch_results['files_processed']) * 100 if batch_results['files_processed'] > 0 else 0
    
    # Find most common issues
    from collections import Counter
    issue_counts = Counter(all_issues)
    batch_results['processing_summary']['common_issues'] = issue_counts.most_common(5)
    
    progress_bar.progress(1.0)
    status_text.text("Processing complete!")
    
    return batch_results

def create_nielsen_distribution_chart(nielsen_scores: List[float]):
    """Create Nielsen score distribution chart."""
    
    fig = px.histogram(
        x=nielsen_scores,
        bins=20,
        title="Nielsen Score Distribution",
        labels={'x': 'Nielsen Score (%)', 'y': 'Number of Files'},
        color_discrete_sequence=['#667eea']
    )
    
    fig.add_vline(x=50, line_dash="dash", line_color="orange", 
                  annotation_text="Baseline (50%)")
    fig.add_vline(x=75, line_dash="dash", line_color="green", 
                  annotation_text="Target (75%)")
    
    return fig

def create_retailer_comparison_chart(file_details: List[Dict]):
    """Create retailer compatibility comparison."""
    
    df = pd.DataFrame(file_details)
    
    fig = px.scatter(
        df, 
        x='nielsen_score', 
        y='retailer_score',
        hover_data=['filename', 'errors', 'warnings'],
        title="Nielsen vs Retailer Scores",
        labels={'nielsen_score': 'Nielsen Score (%)', 'retailer_score': 'Average Retailer Score (%)'},
        color='compliance_status',
        color_discrete_map={'Pass': 'green', 'Fail': 'red'}
    )
    
    # Add diagonal reference line
    fig.add_trace(go.Scatter(
        x=[0, 100], y=[0, 100],
        mode='lines',
        line=dict(dash='dash', color='gray'),
        name='Perfect Correlation',
        showlegend=False
    ))
    
    return fig

def create_issues_breakdown_chart(file_details: List[Dict]):
    """Create issues breakdown chart."""
    
    df = pd.DataFrame(file_details)
    
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=('Errors by File', 'Warnings by File'),
        specs=[[{"secondary_y": False}, {"secondary_y": False}]]
    )
    
    # Errors
    fig.add_trace(
        go.Bar(x=df['filename'], y=df['errors'], name='Errors', marker_color='red'),
        row=1, col=1
    )
    
    # Warnings
    fig.add_trace(
        go.Bar(x=df['filename'], y=df['warnings'], name='Warnings', marker_color='orange'),
        row=1, col=2
    )
    
    fig.update_layout(
        title_text="Validation Issues by File",
        showlegend=False
    )
    
    # Rotate x-axis labels if many files
    if len(df) > 5:
        fig.update_xaxes(tickangle=45)
    
    return fig

def generate_batch_report(batch_results: Dict) -> str:
    """Generate downloadable batch report."""
    
    report = f"""
# MetaOps Validator Batch Report
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Summary
- Files Processed: {batch_results['files_processed']}
- Average Nielsen Score: {batch_results['processing_summary']['avg_nielsen_score']:.1f}%
- Average Retailer Score: {batch_results['processing_summary']['avg_retailer_score']:.1f}%
- Compliance Rate: {batch_results['processing_summary']['compliance_rate']:.1f}%
- Total Errors: {batch_results['total_errors']}
- Total Warnings: {batch_results['total_warnings']}

## File Details
"""
    
    for file_detail in batch_results['file_details']:
        report += f"""
### {file_detail['filename']}
- Nielsen Score: {file_detail['nielsen_score']}%
- Retailer Score: {file_detail['retailer_score']}%
- Compliance: {file_detail['compliance_status']}
- Errors: {file_detail['errors']}, Warnings: {file_detail['warnings']}
- Missing Critical Fields: {file_detail['missing_critical']}
- Sales Impact: {file_detail['sales_impact']}
- Best Retailer Fit: {file_detail['best_retailer']}
- Needs Work: {file_detail['worst_retailer']}
"""
    
    if batch_results['processing_summary']['common_issues']:
        report += "\n## Most Common Issues\n"
        for issue, count in batch_results['processing_summary']['common_issues']:
            report += f"- {issue}: {count} occurrences\n"
    
    return report

def main():
    """Main dashboard application."""
    
    # Header
    st.title("📊 MetaOps Validator Dashboard")
    st.markdown("*Advanced analytics and batch processing for ONIX validation*")
    
    # Sidebar
    st.sidebar.header("🎛️ Dashboard Controls")
    
    # Mode selection
    mode = st.sidebar.selectbox(
        "Select Mode",
        ["Single File Analysis", "Batch Processing", "Historical Analytics"],
        help="Choose analysis mode: Single file for individual validation, Batch for multiple files with analytics, Historical for trend analysis"
    )
    
    if mode == "Single File Analysis":
        st.markdown("### 📄 Single File Analysis")
        st.info("For single file validation, please use the main validation interface.")
        if st.button("🔗 Go to Main Validator"):
            st.markdown("[Click here to access the main validator](http://localhost:8502)")
    
    elif mode == "Batch Processing":
        st.markdown("### 📁 Batch Processing")
        st.write("Upload multiple ONIX files for comprehensive analysis.")
        
        # Batch file upload
        uploaded_files = st.file_uploader(
            "Upload ONIX Files",
            type=['xml'],
            accept_multiple_files=True,
            help="Select multiple ONIX XML files for batch processing"
        )
        
        if uploaded_files and len(uploaded_files) > 0:
            st.success(f"✅ {len(uploaded_files)} files uploaded")
            
            # Processing options
            st.subheader("📋 Processing Options")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                include_nielsen = st.checkbox("Nielsen Scoring", value=True)
            with col2:
                include_retailer = st.checkbox("Retailer Analysis", value=True)
            with col3:
                include_validation = st.checkbox("Full Validation", value=True)
            
            # Process batch
            if st.button("🚀 Process Batch", type="primary"):
                st.markdown("---")
                st.subheader("🔄 Processing Results")
                
                batch_results = process_batch_files(uploaded_files)
                
                # Display summary metrics
                st.subheader("📈 Batch Summary", help="Overview of batch processing results with key performance indicators")
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric(
                        "Files Processed", 
                        batch_results['files_processed'],
                        help="Number of ONIX files successfully analyzed in this batch"
                    )
                
                with col2:
                    avg_nielsen = batch_results['processing_summary']['avg_nielsen_score']
                    st.metric(
                        "Avg Nielsen Score", 
                        f"{avg_nielsen:.1f}%",
                        help="Average metadata completeness score across all files. 75%+ indicates excellent quality."
                    )
                
                with col3:
                    compliance_rate = batch_results['processing_summary']['compliance_rate']
                    st.metric(
                        "Compliance Rate", 
                        f"{compliance_rate:.1f}%",
                        help="Percentage of files passing validation without critical errors. 100% is the goal."
                    )
                
                with col4:
                    total_issues = batch_results['total_errors'] + batch_results['total_warnings']
                    st.metric(
                        "Total Issues", 
                        total_issues,
                        help="Combined count of errors and warnings across all processed files"
                    )
                
                # Visualizations
                st.markdown("---")
                st.subheader("📊 Analytics Charts")
                
                # Nielsen distribution
                if batch_results['nielsen_scores']:
                    nielsen_chart = create_nielsen_distribution_chart(batch_results['nielsen_scores'])
                    st.plotly_chart(nielsen_chart, use_container_width=True)
                
                # Retailer comparison
                if batch_results['file_details']:
                    retailer_chart = create_retailer_comparison_chart(batch_results['file_details'])
                    st.plotly_chart(retailer_chart, use_container_width=True)
                
                # Issues breakdown
                if batch_results['file_details']:
                    issues_chart = create_issues_breakdown_chart(batch_results['file_details'])
                    st.plotly_chart(issues_chart, use_container_width=True)
                
                # Detailed results table
                st.markdown("---")
                st.subheader("📋 Detailed Results")
                
                df = pd.DataFrame(batch_results['file_details'])
                st.dataframe(df, use_container_width=True)
                
                # Common issues
                if batch_results['processing_summary']['common_issues']:
                    st.subheader("⚠️ Most Common Issues")
                    for issue, count in batch_results['processing_summary']['common_issues']:
                        st.write(f"• **{issue}** - {count} occurrences")
                
                # Download report
                st.markdown("---")
                st.subheader("💾 Export Results")
                
                report_content = generate_batch_report(batch_results)
                st.download_button(
                    label="📄 Download Report",
                    data=report_content,
                    file_name=f"metaops_batch_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
                    mime="text/markdown"
                )
                
                # Export CSV
                csv_buffer = io.StringIO()
                df.to_csv(csv_buffer, index=False)
                st.download_button(
                    label="📊 Download CSV Data",
                    data=csv_buffer.getvalue(),
                    file_name=f"metaops_batch_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
        else:
            st.info("👆 Upload multiple ONIX files to begin batch processing")
    
    elif mode == "Historical Analytics":
        st.markdown("### 📈 Historical Analytics")
        st.info("📊 Historical analytics would integrate with a database to track validation trends over time.")
        
        # Placeholder for future historical data
        st.markdown("""
        **Future Features:**
        - Validation trend analysis over time
        - Publisher-specific improvement tracking  
        - Retailer requirement evolution monitoring
        - Metadata quality benchmarking
        - Automated quality alerts and notifications
        """)
        
        # Demo chart
        import random
        dates = pd.date_range(start='2024-01-01', end='2024-12-31', freq='W')
        demo_data = {
            'Date': dates,
            'Avg Nielsen Score': [60 + random.randint(-10, 15) for _ in dates],
            'Compliance Rate': [75 + random.randint(-15, 20) for _ in dates]
        }
        
        demo_df = pd.DataFrame(demo_data)
        
        fig = px.line(demo_df, x='Date', y=['Avg Nielsen Score', 'Compliance Rate'],
                      title="Demo: Historical Validation Trends")
        st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    main()