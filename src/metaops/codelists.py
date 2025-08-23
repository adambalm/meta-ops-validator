# EDItEUR ONIX Codelist utilities (deterministic, LLM-free)
# Loads official EDItEUR codelists for semantic validation

import csv
from pathlib import Path
from typing import Dict, List, Optional, Set
import json
from lxml import etree

class CodelistManager:
    """Manages EDItEUR ONIX codelists for deterministic validation."""

    def __init__(self, codelists_dir: Path):
        self.codelists_dir = codelists_dir
        self._loaded_lists: Dict[str, Dict[str, str]] = {}
        self._xml_parsed = False
        self._xml_codelists: Dict[str, Dict[str, str]] = {}

    def _load_xml_codelists(self):
        """Load all codelists from the official EDItEUR XML file."""
        if self._xml_parsed:
            return

        xml_path = self.codelists_dir / "ONIX_BookProduct_Codelists_Issue_70.xml"
        if not xml_path.exists():
            print(f"Warning: XML codelists file not found at {xml_path}")
            return

        try:
            tree = etree.parse(str(xml_path))
            root = tree.getroot()

            # Parse each CodeList
            for codelist in root.xpath("//CodeList"):
                list_number = codelist.xpath("CodeListNumber/text()")[0]
                list_desc = codelist.xpath("CodeListDescription/text()")[0] if codelist.xpath("CodeListDescription/text()") else f"List {list_number}"

                codes = {}
                for code in codelist.xpath("Code"):
                    code_value = code.xpath("CodeValue/text()")[0] if code.xpath("CodeValue/text()") else None
                    code_desc = code.xpath("CodeDescription/text()")[0] if code.xpath("CodeDescription/text()") else ""

                    # Check if deprecated
                    deprecated = code.xpath("DeprecatedNumber/text()")
                    if deprecated and deprecated[0]:
                        code_desc += " [DEPRECATED]"

                    if code_value:
                        codes[code_value] = code_desc

                # Store with multiple key formats for flexibility
                self._xml_codelists[list_number] = codes
                self._xml_codelists[f"List{list_number}"] = codes
                self._xml_codelists[f"list_{list_number}"] = codes

            self._xml_parsed = True
            print(f"Loaded {len(self._xml_codelists)//3} codelists from official EDItEUR XML")

        except Exception as e:
            print(f"Warning: Could not parse XML codelists: {e}")

    def load_codelist(self, list_name: str, csv_filename: Optional[str] = None) -> Dict[str, str]:
        """Load a codelist. Tries XML first, falls back to CSV. Returns dict of {code: description}."""
        if list_name in self._loaded_lists:
            return self._loaded_lists[list_name]

        # Try loading from XML first
        self._load_xml_codelists()
        if list_name in self._xml_codelists:
            self._loaded_lists[list_name] = self._xml_codelists[list_name]
            return self._xml_codelists[list_name]

        # Fallback to CSV loading (legacy support)
        return self._load_csv_codelist(list_name, csv_filename)

    def _load_csv_codelist(self, list_name: str, csv_filename: Optional[str] = None) -> Dict[str, str]:
        """Load a codelist from CSV file (fallback method)."""
        if csv_filename is None:
            csv_filename = f"{list_name.lower()}.csv"

        csv_path = self.codelists_dir / csv_filename

        if not csv_path.exists():
            # Return empty dict if codelist file not found (graceful degradation)
            self._loaded_lists[list_name] = {}
            return {}

        try:
            codelist = {}
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # Common EDItEUR CSV structure: Code, Description
                    code = row.get('Code') or row.get('code') or row.get('Value')
                    desc = row.get('Description') or row.get('description') or row.get('Meaning')
                    if code and desc:
                        codelist[code.strip()] = desc.strip()

            self._loaded_lists[list_name] = codelist
            return codelist

        except Exception as e:
            # Log error but don't crash validation
            print(f"Warning: Could not load codelist {list_name}: {e}")
            self._loaded_lists[list_name] = {}
            return {}

    def is_valid_code(self, list_name: str, code: str) -> bool:
        """Check if a code is valid in the specified codelist."""
        codelist = self.load_codelist(list_name)
        return code in codelist

    def get_code_description(self, list_name: str, code: str) -> Optional[str]:
        """Get human-readable description for a code."""
        codelist = self.load_codelist(list_name)
        return codelist.get(code)

# ONIX semantic helpers (deterministic business logic)
# These functions replace the toy validation with proper codelist lookups

def is_audio_product(product_form: str, form_details: List[str] = None) -> bool:
    """
    Determine if product is audio format using official EDItEUR codes.
    Uses official ProductForm (List 150) and ProductFormDetail (List 175) codelists.
    """
    form_details = form_details or []
    manager = get_codelist_manager()

    # Load product form codelist and check description for audio keywords
    product_forms = manager.load_codelist("150")  # List 150: Product form
    if product_form in product_forms:
        desc = product_forms[product_form].lower()
        if any(keyword in desc for keyword in ['audio', 'cd', 'cassette', 'mp3', 'sound recording']):
            return True

    # Check form details for audio indicators
    form_details_list = manager.load_codelist("175")  # List 175: Product form detail
    for detail in form_details:
        if detail in form_details_list:
            desc = form_details_list[detail].lower()
            if any(keyword in desc for keyword in ['audio', 'mp3', 'wav', 'sound']):
                return True

    return False

def is_ebook_product(product_form: str, form_details: List[str] = None) -> bool:
    """
    Determine if product is ebook format using official EDItEUR codes.
    Uses official ProductForm (List 150) and ProductFormDetail (List 175) codelists.
    """
    form_details = form_details or []
    manager = get_codelist_manager()

    # Load product form codelist and check description for ebook keywords
    product_forms = manager.load_codelist("150")  # List 150: Product form
    if product_form in product_forms:
        desc = product_forms[product_form].lower()
        if any(keyword in desc for keyword in ['digital', 'electronic', 'ebook', 'e-book', 'pdf', 'epub']):
            return True

    # Check form details for ebook indicators
    form_details_list = manager.load_codelist("175")  # List 175: Product form detail
    for detail in form_details:
        if detail in form_details_list:
            desc = form_details_list[detail].lower()
            if any(keyword in desc for keyword in ['pdf', 'epub', 'mobi', 'kindle', 'digital']):
                return True

    return False

def get_territory_countries(territory_element, namespace_map: Dict[str, str]) -> tuple[Set[str], Set[str]]:
    """
    Extract included and excluded countries from ONIX Territory composite.

    NOTE: This is a PLACEHOLDER. Real implementation needs:
    - Proper namespace-aware XPath queries
    - CountryCode codelist (List 91)
    - RegionCode handling
    - CountriesIncluded/CountriesExcluded parsing

    Returns: (included_countries, excluded_countries)
    """
    # PLACEHOLDER implementation
    # TODO: Implement real ONIX Territory composite parsing
    included = set()
    excluded = set()

    try:
        # Real ONIX structure:
        # <Territory>
        #   <CountriesIncluded>US GB</CountriesIncluded>
        #   <CountriesExcluded>CA</CountriesExcluded>
        # </Territory>

        # This is TOY logic - replace with proper composite parsing
        if hasattr(territory_element, 'text') and territory_element.text:
            # Toy format: <Territory>US CA</Territory>
            countries = territory_element.text.strip().split()
            included.update(countries)

    except Exception:
        pass

    return included, excluded

# Initialize global codelist manager (will be loaded lazily)
_codelist_manager: Optional[CodelistManager] = None

def get_codelist_manager() -> CodelistManager:
    """Get global codelist manager instance."""
    global _codelist_manager
    if _codelist_manager is None:
        codelists_dir = Path(__file__).parent.parent.parent / "data" / "editeur" / "codelists"
        _codelist_manager = CodelistManager(codelists_dir)
    return _codelist_manager

def validate_with_codelists(code: str, list_name: str) -> tuple[bool, Optional[str]]:
    """
    Validate a code against official EDItEUR codelist.

    Returns: (is_valid, description_or_error)
    """
    manager = get_codelist_manager()

    if manager.is_valid_code(list_name, code):
        desc = manager.get_code_description(list_name, code)
        return True, desc
    else:
        return False, f"Code '{code}' not found in {list_name}"

def get_available_codelists() -> Dict[str, str]:
    """Get all available codelists with their descriptions."""
    manager = get_codelist_manager()
    manager._load_xml_codelists()

    # Extract unique list numbers and descriptions
    available = {}
    for key in manager._xml_codelists.keys():
        if key.isdigit():  # Only numeric list numbers
            # Try to get description from XML if available
            # For now, use basic description
            available[key] = f"ONIX List {key}"

    return available
