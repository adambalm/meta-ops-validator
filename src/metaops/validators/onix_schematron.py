# IMPORTANT: This Schematron validator uses TOY RULES for demo purposes.
# Real ONIX Schematron rules must:
# 1. Use proper ONIX namespaces (reference/short-tag variants)
# 2. Reference official EDItEUR codelists and composites
# 3. Handle territory, date, and product form logic correctly

from pathlib import Path
from typing import List, Dict
from lxml import etree
from lxml.isoschematron import Schematron
from metaops.onix_utils import detect_onix_namespace

def validate_schematron(onix_path: Path, sch_path: Path) -> List[Dict]:
    xml_doc = etree.parse(str(onix_path))
    sch_doc = etree.parse(str(sch_path))
    schematron = Schematron(sch_doc, store_report=True)
    results: List[Dict] = []
    schematron.validate(xml_doc)
    report = schematron.validation_report
    if report is not None:
        for failed in report.findall(".//{http://purl.oclc.org/dsdl/svrl}failed-assert"):
            results.append({
                "type": "schematron",
                "test": failed.get("test"),
                "location": failed.get("location"),
                "message": "".join(failed.itertext()).strip()
            })
        for diag in report.findall(".//{http://purl.oclc.org/dsdl/svrl}successful-report"):
            results.append({
                "type": "schematron-report",
                "test": diag.get("test"),
                "location": diag.get("location"),
                "message": "".join(diag.itertext()).strip()
            })
    return results