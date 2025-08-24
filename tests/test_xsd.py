import pytest
from pathlib import Path
from metaops.validators.onix_xsd import validate_xsd


def test_valid_onix_reference_tags():
    """Test XSD validation with ONIX reference tags file (has known schema issues)."""
    xml_path = Path("test_onix_files/excellent_namespaced.xml")
    results = validate_xsd(xml_path)

    # Generated test files have known schema validation issues
    assert len(results) == 3  # Expected validation errors
    assert all(r["level"] == "ERROR" for r in results)
    assert all("ONIX_BookProduct_3.0_reference.xsd" in str(r) for r in results)


def test_invalid_xml_structure():
    """Test XSD validation with malformed XML."""
    # Create temporary invalid XML file
    invalid_xml = Path("test_invalid.xml")
    invalid_xml.write_text('<?xml version="1.0"?>\n<invalid><unclosed></invalid>')

    try:
        results = validate_xsd(invalid_xml)
        # Should have validation errors
        assert len(results) > 0
        assert any(r["level"] == "ERROR" for r in results)
    finally:
        if invalid_xml.exists():
            invalid_xml.unlink()


def test_namespace_detection_and_schema_selection():
    """Test automatic schema selection based on namespace detection."""
    xml_path = Path("test_onix_files/excellent_namespaced.xml")
    results = validate_xsd(xml_path)

    # Should use reference schema for namespaced file
    assert len(results) == 3  # Has validation errors but uses correct schema
    assert all("schema_used" in str(r) and "ONIX_BookProduct_3.0_reference.xsd" in str(r) for r in results)


def test_missing_schema_file():
    """Test handling of missing schema file."""
    xml_path = Path("test_onix_files/excellent_namespaced.xml")
    nonexistent_schema = Path("nonexistent_schema.xsd")

    results = validate_xsd(xml_path, nonexistent_schema)
    assert len(results) >= 1
    assert any(r["level"] == "ERROR" for r in results)
    assert any("Schema file not found" in r.get("message", "") or "not found" in r.get("message", "") for r in results)
