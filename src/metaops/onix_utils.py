# ONIX utilities for namespace detection and real vs toy validation
from pathlib import Path
from typing import Dict, Optional, Tuple
from lxml import etree

# Official ONIX 3.x namespace URIs
ONIX_REFERENCE_NS = "http://ns.editeur.org/onix/3.0/reference"
ONIX_SHORT_NS = "http://ns.editeur.org/onix/3.0/short"

def detect_onix_namespace(xml_path: Path) -> Tuple[Optional[str], bool]:
    """
    Detect ONIX namespace variant and whether this is a real ONIX file.
    
    Returns:
        (namespace_uri, is_real_onix)
        - namespace_uri: ONIX_REFERENCE_NS, ONIX_SHORT_NS, or None
        - is_real_onix: True if official ONIX namespace detected, False for toy XML
    """
    try:
        xml_doc = etree.parse(str(xml_path))
        root = xml_doc.getroot()
        
        # Check for official ONIX namespaces
        if root.tag.startswith("{" + ONIX_REFERENCE_NS + "}"):
            return ONIX_REFERENCE_NS, True
        elif root.tag.startswith("{" + ONIX_SHORT_NS + "}"):
            return ONIX_SHORT_NS, True
        elif root.nsmap and ONIX_REFERENCE_NS in root.nsmap.values():
            return ONIX_REFERENCE_NS, True
        elif root.nsmap and ONIX_SHORT_NS in root.nsmap.values():
            return ONIX_SHORT_NS, True
        
        # Check if it's our toy format (no namespace, but ONIX structure)
        if root.tag == "ONIX" and not root.nsmap:
            return None, False
            
        return None, False
    except Exception:
        return None, False

def get_namespace_map(namespace_uri: Optional[str]) -> Dict[str, str]:
    """Get namespace map for XPath queries."""
    if namespace_uri == ONIX_REFERENCE_NS:
        return {"onix": ONIX_REFERENCE_NS}
    elif namespace_uri == ONIX_SHORT_NS:
        return {"onix": ONIX_SHORT_NS}
    else:
        # Toy format - no namespaces
        return {}

def is_using_toy_schemas(xsd_path: Path, sch_path: Optional[Path] = None) -> bool:
    """
    Check if we're using toy validation schemas instead of official ones.
    
    This is a safety check to warn users when toy schemas are used with real ONIX.
    """
    # Check if XSD is in our toy samples directory
    if "samples/onix_samples" in str(xsd_path):
        return True
        
    # Check XSD content for our toy schema markers
    try:
        xsd_content = xsd_path.read_text(encoding="utf-8")
        if 'elementFormDefault="qualified"' in xsd_content and "ONIX" in xsd_content:
            # This is likely our toy schema if it doesn't have ONIX namespace
            if ONIX_REFERENCE_NS not in xsd_content and ONIX_SHORT_NS not in xsd_content:
                return True
    except Exception:
        pass
        
    return False