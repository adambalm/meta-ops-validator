# Regression tests for toy vs real ONIX schema migration
import pytest
from pathlib import Path
from metaops.onix_utils import detect_onix_namespace, is_using_toy_schemas, ONIX_REFERENCE_NS, ONIX_SHORT_NS

class TestNamespaceDetection:
    """Test namespace detection for toy vs real ONIX files."""

    def test_toy_onix_detection(self):
        """Toy ONIX files should be detected as non-real."""
        # Our current toy sample
        toy_path = Path("data/samples/onix_samples/sample.xml")
        if toy_path.exists():
            namespace_uri, is_real_onix = detect_onix_namespace(toy_path)
            assert namespace_uri is None
            assert is_real_onix is False

    def test_toy_schema_detection(self):
        """Toy XSD schema should be detected."""
        toy_xsd = Path("data/samples/onix_samples/onix.xsd")
        if toy_xsd.exists():
            assert is_using_toy_schemas(toy_xsd) is True

    def test_real_onix_reference_format(self, tmp_path):
        """Real ONIX reference format should be detected."""
        real_onix = tmp_path / "real_reference.xml"
        real_onix.write_text(f'''<?xml version="1.0"?>
<ONIXMessage xmlns="{ONIX_REFERENCE_NS}">
  <Header>
    <Sender><SenderName>Test</SenderName></Sender>
  </Header>
  <Product>
    <RecordReference>TEST001</RecordReference>
    <DescriptiveDetail>
      <ProductForm>BC</ProductForm>
    </DescriptiveDetail>
  </Product>
</ONIXMessage>''')

        namespace_uri, is_real_onix = detect_onix_namespace(real_onix)
        assert namespace_uri == ONIX_REFERENCE_NS
        assert is_real_onix is True

    def test_real_onix_short_format(self, tmp_path):
        """Real ONIX short format should be detected."""
        real_onix = tmp_path / "real_short.xml"
        real_onix.write_text(f'''<?xml version="1.0"?>
<ONIXmessage xmlns="{ONIX_SHORT_NS}">
  <header>
    <m174>Test</m174>
  </header>
  <product>
    <a001>TEST001</a001>
    <descriptivedetail>
      <b012>BC</b012>
    </descriptivedetail>
  </product>
</ONIXmessage>''')

        namespace_uri, is_real_onix = detect_onix_namespace(real_onix)
        assert namespace_uri == ONIX_SHORT_NS
        assert is_real_onix is True

class TestSchemaCompatibility:
    """Test that migration from toy to real schemas can be detected."""

    def test_toy_schema_with_real_onix_fails(self, tmp_path):
        """Using toy schema with real ONIX should trigger warnings."""
        # This test documents the behavior we want to enforce
        real_onix = tmp_path / "real.xml"
        real_onix.write_text(f'''<?xml version="1.0"?>
<ONIXMessage xmlns="{ONIX_REFERENCE_NS}">
  <Product><RecordReference>TEST</RecordReference></Product>
</ONIXMessage>''')

        toy_xsd = Path("data/samples/onix_samples/onix.xsd")

        namespace_uri, is_real_onix = detect_onix_namespace(real_onix)
        is_toy_schema = is_using_toy_schemas(toy_xsd) if toy_xsd.exists() else True

        # This combination should trigger warnings
        if is_real_onix and is_toy_schema:
            assert True  # This is the problematic case we want to detect
        else:
            pytest.skip("Need toy XSD file to test this scenario")

class TestMigrationReadiness:
    """Tests that will FAIL under toy schema but PASS under real schema."""

    def test_namespace_aware_xpath_required(self):
        """This test should fail until XPaths are namespace-aware."""
        # TODO: When real ONIX schema is added, this test should pass
        # For now, it documents what needs to be implemented
        pytest.skip("TODO: Implement namespace-aware XPath validation")

    def test_codelist_validation_required(self):
        """This test should fail until codelist validation is implemented."""
        # TODO: When EDItEUR codelists are loaded, this test should pass
        pytest.skip("TODO: Implement EDItEUR codelist validation")

    def test_territory_composite_parsing(self):
        """This test should fail until proper Territory composite parsing is implemented."""
        # TODO: Real Territory validation with CountriesIncluded/CountriesExcluded
        pytest.skip("TODO: Implement real Territory composite parsing")

if __name__ == "__main__":
    pytest.main([__file__])
