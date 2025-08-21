# IMPORTANT: This validator currently works with TOY SCHEMAS for demo purposes.
# For production use with real ONIX 3.x files:
# 1. Replace toy XSD with official EDItEUR ONIX 3.x schema
# 2. Handle namespace-aware validation (reference vs short-tag)
# 3. Use official codelists for semantic validation

from pathlib import Path
from typing import List, Dict
from lxml import etree
from metaops.onix_utils import detect_onix_namespace, is_using_toy_schemas

def validate_xsd(onix_path: Path, xsd_path: Path) -> List[Dict]:
    """Validate ONIX XML against XSD schema.
    
    WARNING: Currently uses toy schemas for demo. For production:
    - Use official EDItEUR ONIX 3.x XSD
    - Handle namespace variants (reference/short-tag)
    - Validate against real codelists
    """
    namespace_uri, is_real_onix = detect_onix_namespace(onix_path)
    is_toy_schema = is_using_toy_schemas(xsd_path)
    
    # Safety check: warn if using toy schema with real ONIX
    if is_real_onix and is_toy_schema:
        results = [{
            "line": 1,
            "level": "WARNING", 
            "domain": "SCHEMA_MISMATCH",
            "type": "xsd",
            "message": "Real ONIX file detected but using toy XSD schema. Use official EDItEUR ONIX 3.x schema for production.",
            "path": onix_path.name
        }]
    else:
        results = []
    
    xml_doc = etree.parse(str(onix_path))
    xsd_doc = etree.parse(str(xsd_path))
    schema = etree.XMLSchema(xsd_doc)
    if not schema.validate(xml_doc):
        for e in schema.error_log:
            results.append({
                "line": e.line,
                "level": e.level_name,
                "domain": e.domain_name,
                "type": "xsd",
                "message": e.message,
                "path": onix_path.name
            })
    return results