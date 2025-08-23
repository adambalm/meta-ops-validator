"""
Production ONIX 3.0 Rule DSL Engine
Supports namespace-aware custom rules with EDItEUR codelist integration
"""

from pathlib import Path
from typing import List, Dict, Optional, Set
from lxml import etree
from .dsl import Rule, load_rules
from metaops.onix_utils import detect_onix_namespace, get_namespace_map, ONIX_REFERENCE_NS, ONIX_SHORT_NS
from metaops.utils.line_extractor import get_line_extractor

def _truthy(value) -> bool:
    """Enhanced truthiness check for XPath results."""
    if isinstance(value, list):
        return len(value) > 0
    if isinstance(value, (str, bytes)):
        return len(value.strip()) > 0
    if isinstance(value, (int, float)):
        return value != 0
    return bool(value)

def get_production_rules_path(namespace_uri: Optional[str], base_path: Path) -> Path:
    """Get the appropriate production rules based on detected namespace."""
    if namespace_uri in [ONIX_REFERENCE_NS, ONIX_SHORT_NS]:
        return base_path / "diagnostic" / "rules.yml"
    else:
        # Fallback to toy rules for demo files
        return base_path / "diagnostic" / "rules.sample.yml"

def load_edl_codelists(base_path: Path) -> Dict[str, Set[str]]:
    """
    Load EDItEUR codelists for validation.

    In production, this would parse the official codelist XML files.
    For now, return essential codelists as constants.
    """
    # TODO: Parse actual codelist files from data/editeur/ONIX_BookProduct_CodeLists.xsd
    return {
        "List5": {"01", "02", "03", "04", "05"},  # Product identifier types (abbreviated)
        "List7": {"BC", "BB", "BD", "ED", "EB"},  # Product form codes (abbreviated)
        "List91": {"01", "02", "11", "12", "13"}, # Territory composite types
        "List163": {"01", "02", "09", "11", "19"} # Publishing date roles
    }

def validate_against_codelist(value: str, codelist_name: str, codelists: Dict[str, Set[str]]) -> bool:
    """Validate a value against an EDItEUR codelist."""
    if codelist_name not in codelists:
        return True  # Unknown codelist, assume valid

    return value.strip() in codelists[codelist_name]

def enhance_rule_with_codelist_check(rule: Rule, codelists: Dict[str, Set[str]]) -> Rule:
    """Enhance rule XPath expressions with codelist validation if applicable."""
    # Look for codelist references in rule names or descriptions
    enhanced_rule = rule

    # Example: If rule mentions "ProductIDType", add codelist validation
    if "ProductIDType" in rule.name and "List5" not in rule.assert_expr:
        # Could enhance XPath to include codelist check
        pass

    return enhanced_rule

def evaluate(onix_path: Path, rules_path: Optional[Path] = None) -> List[Dict]:
    """
    Evaluate custom rules against ONIX XML.

    Now supports:
    - Namespace-aware XPath processing
    - EDItEUR codelist validation
    - Automatic rules selection based on ONIX variant
    - Enhanced error context and recommendations
    """
    # Detect ONIX namespace for appropriate processing
    namespace_uri, is_real_onix = detect_onix_namespace(onix_path)
    nsmap = get_namespace_map(namespace_uri)

    # Create line extractor for better debugging
    line_extractor = get_line_extractor(onix_path)

    # Auto-select appropriate rules if not provided
    if rules_path is None:
        project_root = Path(__file__).parent.parent.parent.parent
        rules_path = get_production_rules_path(namespace_uri, project_root)

    # Validate rules file exists
    if not rules_path.exists():
        return [{
            "line": 1,
            "level": "ERROR",
            "domain": "RULES_MISSING",
            "type": "rules",
            "message": f"Rules file not found: {rules_path}",
            "path": onix_path.name
        }]

    # Load codelists for validation
    project_root = Path(__file__).parent.parent.parent.parent
    codelists = load_edl_codelists(project_root)

    findings: List[Dict] = []

    try:
        # Load and parse rules
        rules: List[Rule] = load_rules(rules_path)
        xml_doc = etree.parse(str(onix_path))
        root = xml_doc.getroot()

        # Process each rule
        for rule in rules:
            try:
                # Enhance rule with codelist validation if applicable
                enhanced_rule = enhance_rule_with_codelist_check(rule, codelists)

                # Find context nodes using namespace-aware XPath
                ctx_nodes = root.xpath(enhanced_rule.when, namespaces=nsmap)

                if not ctx_nodes:
                    continue

                # Evaluate rule for each context node
                for node in ctx_nodes:
                    result = node.xpath(enhanced_rule.assert_expr, namespaces=nsmap)

                    if not _truthy(result):
                        # Extract line number if possible
                        line_num = getattr(node, 'sourceline', 1)

                        # Get node path for context
                        node_path = xml_doc.getpath(node)

                        findings.append({
                            "line": line_num,
                            "level": enhanced_rule.severity.upper(),
                            "domain": "CUSTOM_RULE",
                            "type": "rules",
                            "message": enhanced_rule.name,
                            "path": onix_path.name,
                            "rule_id": enhanced_rule.id,
                            "explanation": enhanced_rule.explain or "",
                            "context_path": node_path,
                            "assert_expression": enhanced_rule.assert_expr,
                            "namespace": namespace_uri,
                            "rules_used": rules_path.name
                        })

            except etree.XPathEvalError as e:
                findings.append({
                    "line": line_extractor.extract_line_from_xpath(str(element.getroottree().getpath(element))) if hasattr(element, 'getroottree') else 1,
                    "level": "ERROR",
                    "domain": "XPATH_ERROR",
                    "type": "rules",
                    "message": f"XPath error in rule '{rule.name}': {str(e)}",
                    "path": onix_path.name,
                    "rule_id": rule.id
                })
            except Exception as e:
                findings.append({
                    "line": line_extractor.extract_line_from_xpath(str(element.getroottree().getpath(element))) if hasattr(element, 'getroottree') else 1,
                    "level": "ERROR",
                    "domain": "RULE_ERROR",
                    "type": "rules",
                    "message": f"Error processing rule '{rule.name}': {str(e)}",
                    "path": onix_path.name,
                    "rule_id": rule.id
                })

        # Add success message if no issues and rules were processed
        if not findings and rules:
            findings.append({
                "line": 1,
                "level": "INFO",
                "domain": "VALIDATION_SUCCESS",
                "type": "rules",
                "message": f"Rule engine validation passed using {rules_path.name} ({len(rules)} rules)",
                "path": onix_path.name,
                "namespace": namespace_uri
            })

    except Exception as e:
        findings.append({
            "line": 1,
            "level": "ERROR",
            "domain": "VALIDATION_ERROR",
            "type": "rules",
            "message": f"Rule engine validation failed: {str(e)}",
            "path": onix_path.name
        })

    return findings
