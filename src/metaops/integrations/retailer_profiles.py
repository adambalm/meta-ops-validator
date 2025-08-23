#!/usr/bin/env python3
"""
MetaOps Validator - Retailer Integration Profiles
Retailer-specific validation rules and API integration patterns
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from pathlib import Path
import asyncio
import aiohttp
import json
import logging
from lxml import etree

@dataclass
class ValidationRule:
    """Single validation rule for retailer compliance"""
    rule_id: str
    xpath_expression: str
    constraint_type: str  # required|forbidden|format|value
    expected_value: Optional[str] = None
    error_message: str = ""
    severity: str = "error"  # error|warning|info

@dataclass
class RetailerConstraint:
    """Retailer-specific business constraint"""
    constraint_id: str
    category: str  # territory|pricing|format|metadata
    description: str
    validation_rules: List[ValidationRule]
    implementation_notes: str = ""

class RetailerProfile(ABC):
    """Base class for retailer-specific validation profiles"""

    def __init__(self):
        self.retailer_name: str = ""
        self.api_base_url: str = ""
        self.validation_rules: List[ValidationRule] = []
        self.constraints: List[RetailerConstraint] = []
        self.required_namespaces: Dict[str, str] = {}

    @abstractmethod
    async def validate_onix(self, onix_data: str) -> Dict[str, Any]:
        """Validate ONIX against retailer-specific requirements"""
        pass

    @abstractmethod
    async def submit_onix(self, onix_data: str, credentials: Dict) -> Dict[str, Any]:
        """Submit validated ONIX to retailer API"""
        pass

    def get_namespace_aware_xpath(self, xpath: str) -> str:
        """Convert XPath to namespace-aware format"""
        # Replace common ONIX elements with namespace prefixes
        replacements = {
            "//Product": "//onix:Product",
            "//RecordReference": "//onix:RecordReference",
            "//ProductIdentifier": "//onix:ProductIdentifier",
            "//DescriptiveDetail": "//onix:DescriptiveDetail",
            "//PublishingDetail": "//onix:PublishingDetail",
            "//ProductSupply": "//onix:ProductSupply"
        }

        namespace_xpath = xpath
        for old, new in replacements.items():
            namespace_xpath = namespace_xpath.replace(old, new)

        return namespace_xpath

    def evaluate_xpath_rule(self, xml_doc: etree._ElementTree, rule: ValidationRule) -> List[Dict]:
        """Evaluate single XPath rule against ONIX document"""
        findings = []

        try:
            # Use namespace-aware XPath
            ns_xpath = self.get_namespace_aware_xpath(rule.xpath_expression)
            result = xml_doc.xpath(ns_xpath, namespaces=self.required_namespaces)

            if rule.constraint_type == "required" and not result:
                findings.append({
                    "rule_id": rule.rule_id,
                    "severity": rule.severity,
                    "message": rule.error_message or f"Required field missing: {rule.xpath_expression}",
                    "xpath": rule.xpath_expression
                })
            elif rule.constraint_type == "forbidden" and result:
                findings.append({
                    "rule_id": rule.rule_id,
                    "severity": rule.severity,
                    "message": rule.error_message or f"Forbidden field present: {rule.xpath_expression}",
                    "xpath": rule.xpath_expression
                })
            elif rule.constraint_type == "value" and result:
                for element in result:
                    if element.text != rule.expected_value:
                        findings.append({
                            "rule_id": rule.rule_id,
                            "severity": rule.severity,
                            "message": rule.error_message or f"Expected '{rule.expected_value}', found '{element.text}'",
                            "xpath": rule.xpath_expression,
                            "actual_value": element.text
                        })

        except Exception as e:
            findings.append({
                "rule_id": rule.rule_id,
                "severity": "error",
                "message": f"XPath evaluation failed: {str(e)}",
                "xpath": rule.xpath_expression
            })

        return findings

class AmazonKDPProfile(RetailerProfile):
    """Amazon Kindle Direct Publishing validation profile"""

    def __init__(self):
        super().__init__()
        self.retailer_name = "Amazon KDP"
        self.api_base_url = "https://kdp-api.amazon.com/v1"
        self.required_namespaces = {"onix": "http://ns.editeur.org/onix/3.0/reference"}

        # Amazon KDP specific validation rules
        self.validation_rules = [
            ValidationRule(
                rule_id="amazon_isbn_required",
                xpath_expression="//ProductIdentifier[ProductIDType='15']/IDValue",
                constraint_type="required",
                error_message="ISBN-13 is required for Amazon KDP submissions"
            ),
            ValidationRule(
                rule_id="amazon_territory_us_only",
                xpath_expression="//ProductSupply/Market/Territory/CountriesIncluded",
                constraint_type="value",
                expected_value="US",
                error_message="Amazon KDP requires US territory restriction",
                severity="warning"
            ),
            ValidationRule(
                rule_id="amazon_digital_format_required",
                xpath_expression="//ProductForm",
                constraint_type="value",
                expected_value="ED",  # Digital/Electronic
                error_message="Amazon KDP requires digital format designation"
            ),
            ValidationRule(
                rule_id="amazon_no_physical_dimensions",
                xpath_expression="//Measure[MeasureType='01']",  # Height
                constraint_type="forbidden",
                error_message="Physical dimensions not allowed for digital publications",
                severity="warning"
            )
        ]

        # Business constraints
        self.constraints = [
            RetailerConstraint(
                constraint_id="amazon_pricing_minimum",
                category="pricing",
                description="Amazon KDP minimum pricing requirements",
                validation_rules=[
                    ValidationRule(
                        rule_id="amazon_min_price_99cents",
                        xpath_expression="//Price[PriceType='02']/PriceAmount",
                        constraint_type="format",
                        error_message="Minimum price for Amazon KDP is $0.99"
                    )
                ]
            ),
            RetailerConstraint(
                constraint_id="amazon_content_restrictions",
                category="metadata",
                description="Amazon content policy compliance",
                validation_rules=[
                    ValidationRule(
                        rule_id="amazon_adult_content_warning",
                        xpath_expression="//AudienceCode",
                        constraint_type="value",
                        expected_value="01",  # General/trade
                        error_message="Adult content requires special handling",
                        severity="warning"
                    )
                ]
            )
        ]

    async def validate_onix(self, onix_data: str) -> Dict[str, Any]:
        """Validate ONIX against Amazon KDP requirements"""
        findings = []

        try:
            # Parse ONIX XML
            xml_doc = etree.fromstring(onix_data.encode())
            doc_tree = etree.ElementTree(xml_doc)

            # Run all validation rules
            for rule in self.validation_rules:
                rule_findings = self.evaluate_xpath_rule(doc_tree, rule)
                findings.extend(rule_findings)

            # Additional Amazon-specific checks
            findings.extend(await self._check_amazon_specific_requirements(doc_tree))

            return {
                "retailer": self.retailer_name,
                "validation_status": "passed" if not any(f["severity"] == "error" for f in findings) else "failed",
                "findings": findings,
                "total_errors": len([f for f in findings if f["severity"] == "error"]),
                "total_warnings": len([f for f in findings if f["severity"] == "warning"])
            }

        except Exception as e:
            return {
                "retailer": self.retailer_name,
                "validation_status": "failed",
                "error": f"Validation failed: {str(e)}",
                "findings": []
            }

    async def _check_amazon_specific_requirements(self, xml_doc: etree._ElementTree) -> List[Dict]:
        """Amazon-specific business logic validation"""
        findings = []

        # Check for DRM-protected content indicators
        drm_indicators = xml_doc.xpath("//EpubTechnicalProtection", namespaces=self.required_namespaces)
        if drm_indicators:
            for indicator in drm_indicators:
                if indicator.text in ["01", "02"]:  # DRM protected
                    findings.append({
                        "rule_id": "amazon_drm_warning",
                        "severity": "warning",
                        "message": "DRM protection detected - ensure Amazon KDP compatibility",
                        "xpath": "//EpubTechnicalProtection"
                    })

        # Check publication date for pre-orders
        pub_dates = xml_doc.xpath("//PublishingDate[PublishingDateRole='01']/Date", namespaces=self.required_namespaces)
        if pub_dates:
            # TODO: Implement date parsing and future date checking
            pass

        return findings

    async def submit_onix(self, onix_data: str, credentials: Dict) -> Dict[str, Any]:
        """Submit ONIX to Amazon KDP API"""
        try:
            # Validate credentials
            if "api_key" not in credentials or "secret_key" not in credentials:
                return {
                    "status": "failed",
                    "error": "Missing Amazon KDP API credentials"
                }

            # TODO: Implement actual Amazon KDP API submission
            # This would require:
            # 1. OAuth authentication with Amazon
            # 2. ONIX to Amazon-specific format conversion
            # 3. API endpoint calls with proper error handling

            # For now, simulate successful submission
            await asyncio.sleep(2)  # Simulate API call

            return {
                "status": "submitted",
                "confirmation_id": f"AMZ-{int(asyncio.get_event_loop().time())}",
                "submission_time": "2024-01-15T10:30:00Z",
                "estimated_processing": "24-48 hours",
                "tracking_url": "https://kdp.amazon.com/submissions/12345"
            }

        except Exception as e:
            return {
                "status": "failed",
                "error": f"Amazon KDP submission failed: {str(e)}"
            }

class IngramSparkProfile(RetailerProfile):
    """IngramSpark distribution validation profile"""

    def __init__(self):
        super().__init__()
        self.retailer_name = "IngramSpark"
        self.api_base_url = "https://api.ingramspark.com/v1"
        self.required_namespaces = {"onix": "http://ns.editeur.org/onix/3.0/reference"}

        # IngramSpark specific validation rules
        self.validation_rules = [
            ValidationRule(
                rule_id="ingram_isbn_required",
                xpath_expression="//ProductIdentifier[ProductIDType='15']/IDValue",
                constraint_type="required",
                error_message="ISBN-13 required for IngramSpark distribution"
            ),
            ValidationRule(
                rule_id="ingram_publisher_name_required",
                xpath_expression="//Publisher/PublisherName",
                constraint_type="required",
                error_message="Publisher name is required for IngramSpark"
            ),
            ValidationRule(
                rule_id="ingram_bisac_subject_required",
                xpath_expression="//Subject[SubjectSchemeIdentifier='10']",  # BISAC
                constraint_type="required",
                error_message="BISAC subject classification required"
            ),
            ValidationRule(
                rule_id="ingram_physical_dimensions",
                xpath_expression="//Measure[MeasureType='01']",  # Height required
                constraint_type="required",
                error_message="Physical dimensions required for print books"
            )
        ]

    async def validate_onix(self, onix_data: str) -> Dict[str, Any]:
        """Validate ONIX against IngramSpark requirements"""
        findings = []

        try:
            xml_doc = etree.fromstring(onix_data.encode())
            doc_tree = etree.ElementTree(xml_doc)

            # Run validation rules
            for rule in self.validation_rules:
                rule_findings = self.evaluate_xpath_rule(doc_tree, rule)
                findings.extend(rule_findings)

            # IngramSpark specific checks
            findings.extend(await self._check_ingram_requirements(doc_tree))

            return {
                "retailer": self.retailer_name,
                "validation_status": "passed" if not any(f["severity"] == "error" for f in findings) else "failed",
                "findings": findings,
                "total_errors": len([f for f in findings if f["severity"] == "error"]),
                "total_warnings": len([f for f in findings if f["severity"] == "warning"])
            }

        except Exception as e:
            return {
                "retailer": self.retailer_name,
                "validation_status": "failed",
                "error": str(e),
                "findings": []
            }

    async def _check_ingram_requirements(self, xml_doc: etree._ElementTree) -> List[Dict]:
        """IngramSpark-specific validation logic"""
        findings = []

        # Check for print vs digital format consistency
        product_form = xml_doc.xpath("//ProductForm/text()", namespaces=self.required_namespaces)
        dimensions = xml_doc.xpath("//Measure[MeasureType='01']", namespaces=self.required_namespaces)

        if product_form and product_form[0] in ["BC", "BB"] and not dimensions:  # Print formats
            findings.append({
                "rule_id": "ingram_print_dimensions_required",
                "severity": "error",
                "message": "Print books require physical dimensions for IngramSpark",
                "xpath": "//Measure"
            })

        return findings

    async def submit_onix(self, onix_data: str, credentials: Dict) -> Dict[str, Any]:
        """Submit ONIX to IngramSpark API"""
        try:
            # TODO: Implement IngramSpark API integration
            await asyncio.sleep(1.5)  # Simulate API call

            return {
                "status": "submitted",
                "confirmation_id": f"ISP-{int(asyncio.get_event_loop().time())}",
                "submission_time": "2024-01-15T10:30:00Z",
                "estimated_processing": "2-4 hours",
                "tracking_url": "https://portal.ingramspark.com/submissions/67890"
            }

        except Exception as e:
            return {
                "status": "failed",
                "error": f"IngramSpark submission failed: {str(e)}"
            }

class MultiRetailerValidator:
    """Concurrent validation across multiple retailer profiles"""

    def __init__(self):
        self.profiles = {
            "amazon_kdp": AmazonKDPProfile(),
            "ingram_spark": IngramSparkProfile()
            # Add more retailers as needed
        }

    async def validate_for_retailers(self, onix_data: str, retailer_names: List[str]) -> Dict[str, Any]:
        """Run validation concurrently for multiple retailers"""
        if "all" in retailer_names:
            retailer_names = list(self.profiles.keys())

        # Create concurrent validation tasks
        tasks = []
        for retailer_name in retailer_names:
            if retailer_name in self.profiles:
                profile = self.profiles[retailer_name]
                task = profile.validate_onix(onix_data)
                tasks.append((retailer_name, task))

        # Execute all validations concurrently
        results = {}
        if tasks:
            task_results = await asyncio.gather(*[task for _, task in tasks], return_exceptions=True)

            for (retailer_name, _), result in zip(tasks, task_results):
                if isinstance(result, Exception):
                    results[retailer_name] = {
                        "validation_status": "failed",
                        "error": str(result)
                    }
                else:
                    results[retailer_name] = result

        # Generate summary
        summary = {
            "total_retailers_checked": len(results),
            "passed": len([r for r in results.values() if r.get("validation_status") == "passed"]),
            "failed": len([r for r in results.values() if r.get("validation_status") == "failed"]),
            "overall_status": "passed" if all(r.get("validation_status") == "passed" for r in results.values()) else "failed"
        }

        return {
            "summary": summary,
            "retailer_results": results
        }

    async def submit_to_retailers(self, onix_data: str, retailer_submissions: Dict[str, Dict]) -> Dict[str, Any]:
        """Submit to multiple retailers with their specific credentials"""
        submission_tasks = []

        for retailer_name, submission_config in retailer_submissions.items():
            if retailer_name in self.profiles:
                profile = self.profiles[retailer_name]
                credentials = submission_config.get("credentials", {})
                task = profile.submit_onix(onix_data, credentials)
                submission_tasks.append((retailer_name, task))

        # Execute submissions concurrently
        results = {}
        if submission_tasks:
            task_results = await asyncio.gather(*[task for _, task in submission_tasks], return_exceptions=True)

            for (retailer_name, _), result in zip(submission_tasks, task_results):
                if isinstance(result, Exception):
                    results[retailer_name] = {
                        "status": "failed",
                        "error": str(result)
                    }
                else:
                    results[retailer_name] = result

        return results

# Factory function for getting retailer profiles
def get_retailer_profile(retailer_name: str) -> Optional[RetailerProfile]:
    """Get specific retailer profile by name"""
    profiles = {
        "amazon_kdp": AmazonKDPProfile(),
        "ingram_spark": IngramSparkProfile()
    }
    return profiles.get(retailer_name)
