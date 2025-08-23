import pytest
from pathlib import Path
from metaops.rules.engine import evaluate
from metaops.validators.nielsen_scoring import calculate_nielsen_score
from metaops.validators.retailer_profiles import calculate_retailer_score


def test_rules_engine_evaluation():
    """Test custom rules engine with sample ONIX file."""
    xml_path = Path("test_onix_files/excellent_namespaced.xml")

    # Should handle missing rules file gracefully
    results = evaluate(xml_path)

    # Should have some result (success or error about missing rules)
    assert len(results) >= 1
    for result in results:
        assert "line" in result
        assert "level" in result
        assert "message" in result


def test_nielsen_scoring_multiple_products():
    """Test Nielsen scoring processes all products in ONIX file."""
    xml_path = Path("test_onix_files/excellent_namespaced.xml")
    results = calculate_nielsen_score(xml_path)

    assert "overall_score" in results
    assert "products_count" in results
    assert results["products_count"] >= 1
    assert results["overall_score"] >= 0
    assert results["overall_score"] <= 100

    if "products_scores" in results:
        # Each product should have individual scoring
        for product_score in results["products_scores"]:
            assert "overall_score" in product_score
            assert "breakdown" in product_score


def test_retailer_scoring_multiple_products():
    """Test retailer scoring processes all products in ONIX file."""
    xml_path = Path("test_onix_files/excellent_namespaced.xml")
    results = calculate_retailer_score(xml_path, "amazon")

    assert "retailer" in results
    assert "overall_score" in results
    assert "products_count" in results
    assert results["products_count"] >= 1

    if "products_scores" in results:
        # Each product should have individual retailer scoring
        for product_score in results["products_scores"]:
            assert "overall_score" in product_score
            assert "field_breakdown" in product_score


def test_codelist_integration():
    """Test that codelists are loaded and available."""
    from metaops.codelists import get_codelist_manager, validate_with_codelists

    manager = get_codelist_manager()

    # Test loading a standard codelist (Product Form - List 150)
    product_forms = manager.load_codelist("150")
    assert len(product_forms) > 0

    # Test common product form codes
    assert "BC" in product_forms  # Paperback
    assert "BB" in product_forms  # Hardback

    # Test validation function
    is_valid, desc = validate_with_codelists("BC", "150")
    assert is_valid
    assert "paperback" in desc.lower() or "softback" in desc.lower()
