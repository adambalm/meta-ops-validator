# IMPORTANT: Rule DSL engine currently uses TOY XPATH patterns.
# For real ONIX 3.x validation:
# 1. All XPaths must be namespace-aware (//onix:Product/onix:DescriptiveDetail)
# 2. Use official EDItEUR codelists for semantic checks
# 3. Handle ONIX composites (PublishingDate with role, Territory with includes/excludes)
# 4. Replace substring tests with proper codelist lookups

from pathlib import Path
from typing import List, Dict
from lxml import etree
from .dsl import Rule, load_rules
from metaops.onix_utils import detect_onix_namespace, get_namespace_map

def _truthy(value) -> bool:
    if isinstance(value, list): return len(value) > 0
    if isinstance(value, (str, bytes)): return len(value) > 0
    return bool(value)

def evaluate(onix_path: Path, rules_path: Path) -> List[Dict]:
    """Evaluate custom rules against ONIX XML.
    
    WARNING: Current rules use toy XPath patterns without namespaces.
    For production ONIX 3.x files, rules must use namespace-aware XPaths
    and official EDItEUR codelists.
    """
    rules: List[Rule] = load_rules(rules_path)
    xml_doc = etree.parse(str(onix_path))
    root = xml_doc.getroot()
    
    # Detect namespace and get proper nsmap
    namespace_uri, is_real_onix = detect_onix_namespace(onix_path)
    nsmap = get_namespace_map(namespace_uri)
    
    findings: List[Dict] = []
    for r in rules:
        ctx_nodes = root.xpath(r.when, namespaces=nsmap)
        if not ctx_nodes: continue
        for node in ctx_nodes:
            result = node.xpath(r.assert_expr, namespaces=nsmap)
            if not _truthy(result):
                findings.append({
                    "id": r.id,
                    "name": r.name,
                    "severity": r.severity,
                    "explain": r.explain or "",
                    "context_path": xml_doc.getpath(node),
                    "assert": r.assert_expr
                })
    return findings