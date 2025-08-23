import pytest
from pathlib import Path
from metaops.validators.onix_schematron import validate_schematron


def test_valid_onix_schematron_validation():
    """Test Schematron validation with valid ONIX file."""
    xml_path = Path("test_onix_files/excellent_namespaced.xml")
    results = validate_schematron(xml_path)

    # Should have validation success result
    assert len(results) == 1
    assert results[0]["level"] == "INFO"
    assert results[0]["domain"] == "VALIDATION_SUCCESS"
    assert "Schematron validation passed" in results[0]["message"]


def test_schematron_rule_selection():
    """Test automatic Schematron rule selection based on namespace."""
    xml_path = Path("test_onix_files/excellent_namespaced.xml")
    results = validate_schematron(xml_path)

    # Should use production rules for namespaced file
    assert len(results) >= 1
    assert results[0]["rules_used"] == "onix-production-rules.sch"


def test_missing_schematron_file():
    """Test handling of missing Schematron file."""
    xml_path = Path("test_onix_files/excellent_namespaced.xml")
    nonexistent_sch = Path("nonexistent_rules.sch")

    results = validate_schematron(xml_path, nonexistent_sch)
    assert len(results) == 1
    assert results[0]["level"] == "ERROR"
    assert "Schematron rules file not found" in results[0]["message"]


def test_line_number_extraction():
    """Test that line numbers are extracted from Schematron reports."""
    xml_path = Path("test_onix_files/excellent_namespaced.xml")
    results = validate_schematron(xml_path)

    # All results should have line numbers (even if default to 1)
    for result in results:
        assert "line" in result
        assert isinstance(result["line"], int)
        assert result["line"] >= 1
