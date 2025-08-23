"""
Production ONIX 3.0 Schematron Validator
Supports namespace-aware business rule validation with official EDItEUR patterns
"""

from pathlib import Path
from typing import List, Dict, Optional
from lxml import etree
from lxml.isoschematron import Schematron
from metaops.onix_utils import detect_onix_namespace, get_namespace_map, ONIX_REFERENCE_NS, ONIX_SHORT_NS

def get_production_schematron_path(namespace_uri: Optional[str], base_path: Path) -> Path:
    """Get the appropriate production Schematron rules based on detected namespace."""
    if namespace_uri in [ONIX_REFERENCE_NS, ONIX_SHORT_NS]:
        return base_path / "data" / "editeur" / "schematron" / "onix-production-rules.sch"
    else:
        # Fallback to toy rules for demo files
        return base_path / "data" / "samples" / "onix_samples" / "rules.sch"

def validate_schematron(onix_path: Path, sch_path: Optional[Path] = None) -> List[Dict]:
    """
    Validate ONIX XML against Schematron business rules.
    
    Now supports:
    - Namespace-aware rule processing
    - Automatic rule selection based on ONIX variant
    - Enhanced error reporting with context
    """
    results = []
    
    # Detect ONIX namespace for appropriate rule selection
    namespace_uri, is_real_onix = detect_onix_namespace(onix_path)
    
    # Auto-select appropriate Schematron rules if not provided
    if sch_path is None:
        project_root = Path(__file__).parent.parent.parent.parent
        sch_path = get_production_schematron_path(namespace_uri, project_root)
    
    # Validate Schematron file exists
    if not sch_path.exists():
        return [{
            "line": 1,
            "level": "ERROR",
            "domain": "SCHEMATRON_MISSING",
            "type": "schematron",
            "message": f"Schematron rules file not found: {sch_path}",
            "path": onix_path.name
        }]
    
    try:
        # Parse ONIX and Schematron documents
        xml_doc = etree.parse(str(onix_path))
        sch_doc = etree.parse(str(sch_path))
        
        # Create Schematron validator with detailed reporting
        schematron = Schematron(sch_doc, store_report=True, store_xslt=True)
        
        # Perform validation
        is_valid = schematron.validate(xml_doc)
        
        # Process validation report
        report = schematron.validation_report
        if report is not None:
            # Process failed assertions (errors/warnings)
            for failed in report.findall(".//{http://purl.oclc.org/dsdl/svrl}failed-assert"):
                location = failed.get("location", "unknown")
                test = failed.get("test", "")
                role = failed.get("role", "error").lower()
                
                # Extract line number from location if possible
                line_num = extract_line_number_from_location(location)
                
                # Get the failure message
                message_text = "".join(failed.itertext()).strip()
                
                results.append({
                    "line": line_num,
                    "level": "ERROR" if role == "error" else "WARNING" if role == "warning" else "INFO",
                    "domain": "SCHEMATRON_RULE",
                    "type": "schematron",
                    "message": message_text,
                    "path": onix_path.name,
                    "test": test,
                    "location": location,
                    "namespace": namespace_uri,
                    "rules_used": sch_path.name
                })
            
            # Process successful reports (informational)
            for success in report.findall(".//{http://purl.oclc.org/dsdl/svrl}successful-report"):
                location = success.get("location", "unknown")
                test = success.get("test", "")
                role = success.get("role", "info").lower()
                
                line_num = extract_line_number_from_location(location)
                message_text = "".join(success.itertext()).strip()
                
                results.append({
                    "line": line_num,
                    "level": "INFO",
                    "domain": "SCHEMATRON_INFO",
                    "type": "schematron",
                    "message": message_text,
                    "path": onix_path.name,
                    "test": test,
                    "location": location,
                    "namespace": namespace_uri,
                    "rules_used": sch_path.name
                })
        
        # Add success message if no issues found
        if is_valid and not results:
            results.append({
                "line": 1,
                "level": "INFO",
                "domain": "VALIDATION_SUCCESS",
                "type": "schematron",
                "message": f"Schematron validation passed using {sch_path.name}",
                "path": onix_path.name,
                "namespace": namespace_uri
            })
            
    except etree.XMLSyntaxError as e:
        results.append({
            "line": e.lineno if e.lineno else 1,
            "level": "ERROR",
            "domain": "XML_SYNTAX",
            "type": "schematron",
            "message": f"XML syntax error in ONIX or Schematron file: {e.msg}",
            "path": onix_path.name
        })
    except Exception as e:
        results.append({
            "line": 1,
            "level": "ERROR",
            "domain": "VALIDATION_ERROR", 
            "type": "schematron",
            "message": f"Schematron validation failed: {str(e)}",
            "path": onix_path.name
        })
    
    return results

def extract_line_number_from_location(location: str) -> int:
    """Extract line number from XPath location string."""
    try:
        # Location format is typically like "*:*[namespace-uri()='...'][1]"
        # or more complex XPath expressions
        # For now, return 1 as default - could be enhanced with more sophisticated parsing
        if location and "[" in location:
            # Try to extract position indicators that might hint at line numbers
            parts = location.split("[")
            for part in parts:
                if part.isdigit() and "]" in part:
                    num = int(part.split("]")[0])
                    if num > 0:
                        return num
    except:
        pass
    return 1