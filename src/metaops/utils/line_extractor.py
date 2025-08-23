"""
Line Number Extraction Utilities
Provides enhanced line number extraction for better debugging precision.
"""

import re
from typing import Optional, Dict, Any
from lxml import etree
from pathlib import Path


class LineNumberExtractor:
    """Extracts accurate line numbers from XML validation errors and XPath locations."""

    def __init__(self, xml_path: Path):
        self.xml_path = xml_path
        self._xml_tree = None
        self._line_map = None

    def _build_line_map(self):
        """Build a mapping of XPath positions to line numbers."""
        if self._line_map is not None:
            return

        try:
            # Parse with line number information
            parser = etree.XMLParser(strip_cdata=False, recover=False, encoding='utf-8')
            self._xml_tree = etree.parse(str(self.xml_path), parser)

            # Build line mapping
            self._line_map = {}
            for element in self._xml_tree.iter():
                if hasattr(element, 'sourceline') and element.sourceline:
                    xpath = self._xml_tree.getpath(element)
                    self._line_map[xpath] = element.sourceline

        except Exception as e:
            print(f"Warning: Could not build line map for {self.xml_path}: {e}")
            self._line_map = {}

    def extract_line_from_xpath(self, xpath: str) -> int:
        """Extract line number from XPath expression."""
        if not xpath:
            return 1

        self._build_line_map()

        # Direct lookup first
        if xpath in self._line_map:
            return self._line_map[xpath]

        # Try to find closest match
        best_match = None
        best_match_line = 1

        for mapped_xpath, line_num in self._line_map.items():
            # Look for partial matches (element without predicates)
            simplified_xpath = re.sub(r'\[[^\]]+\]', '', xpath)
            simplified_mapped = re.sub(r'\[[^\]]+\]', '', mapped_xpath)

            if simplified_mapped in simplified_xpath or simplified_xpath in simplified_mapped:
                if best_match is None or len(mapped_xpath) > len(best_match):
                    best_match = mapped_xpath
                    best_match_line = line_num

        return best_match_line if best_match else 1

    def extract_line_from_location(self, location: str) -> int:
        """Enhanced extraction from Schematron location strings."""
        if not location:
            return 1

        # First try the XPath approach
        line = self.extract_line_from_xpath(location)
        if line > 1:
            return line

        # Fallback to position-based extraction
        return self._extract_line_from_position_indicators(location)

    def _extract_line_from_position_indicators(self, location: str) -> int:
        """Extract line hints from XPath position indicators."""
        try:
            # Look for position indicators like [1], [2], etc.
            position_pattern = r'\[(\d+)\]'
            matches = re.findall(position_pattern, location)

            if matches:
                # Use the largest position number as a hint
                max_position = max(int(m) for m in matches)
                # This is a rough approximation - position doesn't directly map to line
                return max(1, max_position)

            # Look for element count patterns in location
            # Example: /*:ONIXMessage[1]/*:Product[2] suggests this is the 2nd product
            if '*:Product[' in location:
                product_match = re.search(r'\*:Product\[(\d+)\]', location)
                if product_match:
                    product_num = int(product_match.group(1))
                    # Rough estimate: each product might be ~20-50 lines
                    return max(1, 20 + (product_num - 1) * 30)

        except Exception:
            pass

        return 1

    def extract_line_from_error(self, error_msg: str, xpath: str = "") -> int:
        """Extract line number from XML parser error messages."""
        try:
            # Look for line number in error message
            line_patterns = [
                r'line (\d+)',
                r'Line (\d+)',
                r'at line (\d+)',
                r'position (\d+)',
                r':(\d+):'
            ]

            for pattern in line_patterns:
                match = re.search(pattern, error_msg)
                if match:
                    return int(match.group(1))

            # Fallback to XPath extraction
            if xpath:
                return self.extract_line_from_xpath(xpath)

        except Exception:
            pass

        return 1


def get_line_extractor(xml_path: Path) -> LineNumberExtractor:
    """Get a line number extractor for the given XML file."""
    return LineNumberExtractor(xml_path)


def extract_line_number_enhanced(xml_path: Path, location: str = "",
                                error_msg: str = "") -> int:
    """Enhanced line number extraction with multiple fallback strategies."""
    extractor = get_line_extractor(xml_path)

    # Try different extraction methods
    if location:
        line = extractor.extract_line_from_location(location)
        if line > 1:
            return line

    if error_msg:
        line = extractor.extract_line_from_error(error_msg, location)
        if line > 1:
            return line

    return 1


def create_validation_result_with_line(xml_path: Path, error_msg: str,
                                     location: str = "", level: str = "ERROR",
                                     domain: str = "VALIDATION",
                                     validation_type: str = "unknown") -> Dict[str, Any]:
    """Create a standardized validation result with accurate line number."""
    line_num = extract_line_number_enhanced(xml_path, location, error_msg)

    return {
        "line": line_num,
        "level": level,
        "domain": domain,
        "type": validation_type,
        "message": error_msg,
        "path": xml_path.name,
        "location": location if location else "unknown"
    }
