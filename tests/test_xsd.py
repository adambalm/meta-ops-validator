import pytest
from pathlib import Path
from metaops.validators.onix_xsd import validate_xsd


def test_valid_onix_reference_tags():
    """Test XSD validation with valid ONIX reference tags file."""
    xml_path = Path("test_onix_files/excellent_namespaced.xml")
    results = validate_xsd(xml_path)

    # Should have validation success result
    assert len(results) == 1
    assert results[0]["level"] == "INFO"
    assert results[0]["domain"] == "VALIDATION_SUCCESS"
    assert "XSD validation passed" in results[0]["message"]


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
    assert len(results) == 1
    assert "ONIX_BookProduct_3.0_reference.xsd" in results[0]["message"]


def test_missing_schema_file():
    """Test handling of missing schema file."""
    xml_path = Path("test_onix_files/excellent_namespaced.xml")
    nonexistent_schema = Path("nonexistent_schema.xsd")

    results = validate_xsd(xml_path, nonexistent_schema)
    assert len(results) == 1
    assert results[0]["level"] == "ERROR"
    assert "Schema file not found" in results[0]["message"]
