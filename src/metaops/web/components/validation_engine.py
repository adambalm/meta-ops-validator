"""
Validation engine integration for Streamlit web interface.
"""

import tempfile
from pathlib import Path
from typing import Dict, Any, List, Optional
import streamlit as st

# Import validation functions
from metaops.validators.onix_xsd import validate_xsd
from metaops.validators.onix_schematron import validate_schematron
from metaops.validators.nielsen_scoring import calculate_nielsen_score
from metaops.validators.retailer_profiles import calculate_multi_retailer_score
from metaops.rules.engine import evaluate as eval_rules


class ValidationRunner:
    """Runs validation pipeline and manages results."""

    def __init__(self):
        self.results = {}
        self.temp_files = []

    def run_validation_pipeline(self, uploaded_file, options: Dict[str, Any]) -> Dict[str, Any]:
        """Run the complete validation pipeline based on selected options."""
        results = {
            "xsd_results": [],
            "schematron_results": [],
            "rules_results": [],
            "nielsen_data": {},
            "retailer_data": {},
            "pipeline_summary": {
                "stages_completed": [],
                "total_findings": 0,
                "errors": 0,
                "warnings": 0,
                "info": 0
            }
        }

        # Save uploaded file temporarily
        temp_file = self._save_temp_file(uploaded_file)
        if not temp_file:
            st.error("Failed to process uploaded file")
            return results

        try:
            # XSD Validation
            if options.get("run_xsd", False):
                with st.spinner("Running XSD validation..."):
                    results["xsd_results"] = validate_xsd(temp_file)
                    results["pipeline_summary"]["stages_completed"].append("XSD Schema")

            # Schematron Validation
            if options.get("run_schematron", False):
                with st.spinner("Running Schematron validation..."):
                    results["schematron_results"] = validate_schematron(temp_file)
                    results["pipeline_summary"]["stages_completed"].append("Schematron Rules")

            # Custom Rules
            if options.get("run_rules", False):
                with st.spinner("Running custom rules..."):
                    results["rules_results"] = eval_rules(temp_file)
                    results["pipeline_summary"]["stages_completed"].append("Custom Rules")

            # Nielsen Scoring
            if options.get("run_nielsen", False):
                with st.spinner("Calculating Nielsen completeness score..."):
                    results["nielsen_data"] = calculate_nielsen_score(temp_file)
                    results["pipeline_summary"]["stages_completed"].append("Nielsen Scoring")

            # Retailer Analysis
            if options.get("run_retailer", False) and options.get("selected_retailers"):
                with st.spinner("Analyzing retailer compatibility..."):
                    results["retailer_data"] = calculate_multi_retailer_score(
                        temp_file,
                        options["selected_retailers"]
                    )
                    results["pipeline_summary"]["stages_completed"].append("Retailer Analysis")

            # Calculate summary statistics
            self._calculate_pipeline_summary(results)

        except Exception as e:
            st.error(f"Validation pipeline error: {str(e)}")
            results["pipeline_error"] = str(e)

        finally:
            # Clean up temporary files
            self._cleanup_temp_files()

        return results

    def _save_temp_file(self, uploaded_file) -> Optional[Path]:
        """Save uploaded file to temporary location."""
        try:
            # Create temporary file
            temp_fd, temp_path = tempfile.mkstemp(suffix='.xml')
            temp_file_path = Path(temp_path)

            # Write uploaded file content
            with open(temp_fd, 'wb') as temp_file:
                temp_file.write(uploaded_file.getvalue())

            # Track for cleanup
            self.temp_files.append(temp_file_path)

            return temp_file_path

        except Exception as e:
            st.error(f"Error saving uploaded file: {str(e)}")
            return None

    def _calculate_pipeline_summary(self, results: Dict[str, Any]):
        """Calculate summary statistics across all validation results."""
        all_findings = []

        # Collect all findings
        all_findings.extend(results.get("xsd_results", []))
        all_findings.extend(results.get("schematron_results", []))
        all_findings.extend(results.get("rules_results", []))

        # Count by level
        error_count = sum(1 for f in all_findings if f.get("level") == "ERROR")
        warning_count = sum(1 for f in all_findings if f.get("level") == "WARNING")
        info_count = sum(1 for f in all_findings if f.get("level") == "INFO")

        results["pipeline_summary"].update({
            "total_findings": len(all_findings),
            "errors": error_count,
            "warnings": warning_count,
            "info": info_count
        })

    def _cleanup_temp_files(self):
        """Clean up temporary files."""
        for temp_file in self.temp_files:
            try:
                if temp_file.exists():
                    temp_file.unlink()
            except Exception:
                pass  # Ignore cleanup errors
        self.temp_files.clear()

    def get_validation_status_summary(self, results: Dict[str, Any]) -> Dict[str, str]:
        """Get a summary of validation status for display."""
        summary = {}

        # XSD Status
        xsd_results = results.get("xsd_results", [])
        if xsd_results:
            has_errors = any(r.get("level") == "ERROR" for r in xsd_results)
            summary["XSD Validation"] = "❌ Failed" if has_errors else "✅ Passed"

        # Schematron Status
        sch_results = results.get("schematron_results", [])
        if sch_results:
            has_errors = any(r.get("level") == "ERROR" for r in sch_results)
            summary["Schematron Rules"] = "❌ Failed" if has_errors else "✅ Passed"

        # Rules Status
        rules_results = results.get("rules_results", [])
        if rules_results:
            has_errors = any(r.get("level") == "ERROR" for r in rules_results)
            summary["Custom Rules"] = "❌ Failed" if has_errors else "✅ Passed"

        # Nielsen Score
        nielsen_data = results.get("nielsen_data", {})
        if nielsen_data and not nielsen_data.get("error"):
            score = nielsen_data.get("overall_score", 0)
            if score >= 80:
                summary["Nielsen Score"] = f"🟢 {score:.1f}% (Excellent)"
            elif score >= 60:
                summary["Nielsen Score"] = f"🟡 {score:.1f}% (Good)"
            else:
                summary["Nielsen Score"] = f"🔴 {score:.1f}% (Needs Work)"

        # Retailer Compatibility
        retailer_data = results.get("retailer_data", {})
        if retailer_data and not retailer_data.get("error"):
            avg_score = retailer_data.get("average_score", 0)
            if avg_score >= 80:
                summary["Retailer Compatibility"] = f"🟢 {avg_score:.1f}% (High)"
            elif avg_score >= 60:
                summary["Retailer Compatibility"] = f"🟡 {avg_score:.1f}% (Medium)"
            else:
                summary["Retailer Compatibility"] = f"🔴 {avg_score:.1f}% (Low)"

        return summary


def display_pipeline_summary(results: Dict[str, Any]):
    """Display a summary of the validation pipeline results."""
    summary = results.get("pipeline_summary", {})

    if not summary:
        return

    st.subheader("🔍 Validation Summary")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Stages Completed", len(summary.get("stages_completed", [])))

    with col2:
        error_count = summary.get("errors", 0)
        st.metric("Errors", error_count, delta=None if error_count == 0 else -error_count)

    with col3:
        warning_count = summary.get("warnings", 0)
        st.metric("Warnings", warning_count)

    with col4:
        st.metric("Total Findings", summary.get("total_findings", 0))

    # Stages completed
    stages = summary.get("stages_completed", [])
    if stages:
        st.write("**Completed Stages:**", " → ".join(stages))


def display_quick_fix_suggestions(results: Dict[str, Any]):
    """Display quick fix suggestions based on validation results."""
    suggestions = []

    # Analyze results for common issues
    all_findings = []
    all_findings.extend(results.get("xsd_results", []))
    all_findings.extend(results.get("schematron_results", []))
    all_findings.extend(results.get("rules_results", []))

    errors = [f for f in all_findings if f.get("level") == "ERROR"]

    if errors:
        st.subheader("💡 Quick Fix Suggestions")

        # Common error patterns and suggestions
        isbn_errors = [e for e in errors if "isbn" in e.get("message", "").lower()]
        if isbn_errors:
            suggestions.append("📖 **ISBN Issues**: Check that all ISBN values are properly formatted (13 digits without hyphens)")

        namespace_errors = [e for e in errors if "namespace" in e.get("message", "").lower()]
        if namespace_errors:
            suggestions.append("🏷️ **Namespace Issues**: Ensure your ONIX file uses the correct namespace (http://ns.editeur.org/onix/3.0/reference)")

        required_errors = [e for e in errors if "required" in e.get("message", "").lower()]
        if required_errors:
            suggestions.append("✅ **Required Fields**: Add missing required elements like NotificationType, ProductForm, etc.")

        # Nielsen-based suggestions
        nielsen_data = results.get("nielsen_data", {})
        if nielsen_data and not nielsen_data.get("error"):
            missing_critical = nielsen_data.get("missing_critical", [])
            if missing_critical:
                suggestions.append(f"📊 **Completeness**: Add missing high-impact fields: {', '.join(missing_critical[:3])}")

        # Display suggestions
        for suggestion in suggestions:
            st.markdown(suggestion)

        if not suggestions:
            st.info("Run a validation to get specific suggestions for improving your ONIX file.")
