"""
Production ONIX 3.0 XSD Validator
Supports both reference and short-tag ONIX variants with official EDItEUR schemas
"""

from pathlib import Path
from typing import List, Dict, Optional
from lxml import etree
from metaops.onix_utils import detect_onix_namespace, is_using_toy_schemas, ONIX_REFERENCE_NS, ONIX_SHORT_NS

def get_production_schema_path(namespace_uri: Optional[str], base_path: Path) -> Path:
    """Get the appropriate production XSD schema path based on detected namespace."""
    if namespace_uri == ONIX_REFERENCE_NS:
        return base_path / "data" / "editeur" / "ONIX_BookProduct_3.0_reference.xsd"
    elif namespace_uri == ONIX_SHORT_NS:
        return base_path / "data" / "editeur" / "ONIX_BookProduct_3.0_short.xsd"
    else:
        # Fallback to toy schema for non-namespaced files
        return base_path / "data" / "samples" / "onix_samples" / "onix.xsd"

def validate_xsd(onix_path: Path, xsd_path: Optional[Path] = None) -> List[Dict]:
    """
    Validate ONIX XML against appropriate XSD schema.
    
    Now supports:
    - Official EDItEUR ONIX 3.0 schemas (reference and short-tag variants)
    - Automatic schema selection based on namespace detection
    - Fallback to toy schema for demo files
    """
    results = []
    
    # Detect ONIX namespace variant
    namespace_uri, is_real_onix = detect_onix_namespace(onix_path)
    
    # Auto-select appropriate schema if not provided
    if xsd_path is None:
        project_root = Path(__file__).parent.parent.parent.parent
        xsd_path = get_production_schema_path(namespace_uri, project_root)
    
    # Validate schema file exists
    if not xsd_path.exists():
        return [{
            "line": 1,
            "level": "ERROR",
            "domain": "SCHEMA_MISSING",
            "type": "xsd",
            "message": f"XSD schema file not found: {xsd_path}",
            "path": onix_path.name
        }]
    
    is_toy_schema = is_using_toy_schemas(xsd_path)
    
    # Warn if schema mismatch detected
    if is_real_onix and is_toy_schema:
        results.append({
            "line": 1,
            "level": "WARNING", 
            "domain": "SCHEMA_MISMATCH",
            "type": "xsd",
            "message": "Production ONIX file detected but using toy XSD schema. Consider using official EDItEUR schema.",
            "path": onix_path.name,
            "recommendation": f"Use {get_production_schema_path(namespace_uri, Path(__file__).parent.parent.parent.parent)}"
        })
    elif not is_real_onix and not is_toy_schema:
        results.append({
            "line": 1,
            "level": "INFO", 
            "domain": "SCHEMA_INFO",
            "type": "xsd",
            "message": "Using production schema with demo/toy ONIX file.",
            "path": onix_path.name
        })
    
    try:
        # Parse XML and XSD
        xml_doc = etree.parse(str(onix_path))
        xsd_doc = etree.parse(str(xsd_path))
        
        # Create schema validator
        schema = etree.XMLSchema(xsd_doc)
        
        # Perform validation
        is_valid = schema.validate(xml_doc)
        
        if not is_valid:
            # Process validation errors
            for error in schema.error_log:
                results.append({
                    "line": error.line if error.line else 1,
                    "column": error.column if error.column else 1,
                    "level": "ERROR",
                    "domain": error.domain_name or "XSD",
                    "type": "xsd",
                    "message": error.message,
                    "path": onix_path.name,
                    "namespace": namespace_uri,
                    "schema_used": xsd_path.name
                })
        
        # Add success info for clean files
        if is_valid and not results:
            results.append({
                "line": 1,
                "level": "INFO",
                "domain": "VALIDATION_SUCCESS",
                "type": "xsd",
                "message": f"XSD validation passed using {xsd_path.name}",
                "path": onix_path.name,
                "namespace": namespace_uri
            })
            
    except etree.XMLSyntaxError as e:
        results.append({
            "line": e.lineno if e.lineno else 1,
            "column": e.offset if e.offset else 1,
            "level": "ERROR",
            "domain": "XML_SYNTAX",
            "type": "xsd",
            "message": f"XML syntax error: {e.msg}",
            "path": onix_path.name
        })
    except Exception as e:
        results.append({
            "line": 1,
            "level": "ERROR",
            "domain": "VALIDATION_ERROR",
            "type": "xsd", 
            "message": f"XSD validation failed: {str(e)}",
            "path": onix_path.name
        })
    
    return results