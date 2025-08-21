# EDItEUR ONIX Codelist utilities (deterministic, LLM-free)
# Loads official EDItEUR codelists for semantic validation

import csv
from pathlib import Path
from typing import Dict, List, Optional, Set
import json

class CodelistManager:
    """Manages EDItEUR ONIX codelists for deterministic validation."""
    
    def __init__(self, codelists_dir: Path):
        self.codelists_dir = codelists_dir
        self._loaded_lists: Dict[str, Dict[str, str]] = {}
        
    def load_codelist(self, list_name: str, csv_filename: Optional[str] = None) -> Dict[str, str]:
        """Load a codelist from CSV file. Returns dict of {code: description}."""
        if list_name in self._loaded_lists:
            return self._loaded_lists[list_name]
            
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
    
    NOTE: This is a PLACEHOLDER implementation. Real logic requires:
    - Official ProductForm codelist (List 150)  
    - ProductFormDetail codelist (List 175)
    - Proper mapping of audio-related codes
    
    Current implementation uses known common codes but is INCOMPLETE.
    """
    form_details = form_details or []
    
    # PLACEHOLDER: Common audio codes (not exhaustive!)
    # TODO: Replace with official EDItEUR codelist lookup
    audio_forms = {'AB', 'AC', 'AD', 'AE', 'AF', 'AG', 'AH', 'AI', 'AJ', 'AK', 'AL', 'AM', 'AN'}
    audio_details = {'A101', 'A102', 'A103', 'A104', 'A105', 'A201', 'A202', 'A203', 'A204', 'A205'}
    
    if product_form in audio_forms:
        return True
        
    # Check form details for audio indicators
    return any(detail in audio_details for detail in form_details)

def is_ebook_product(product_form: str, form_details: List[str] = None) -> bool:
    """
    Determine if product is ebook format using official EDItEUR codes.
    
    NOTE: PLACEHOLDER - needs official codelist integration.
    """
    form_details = form_details or []
    
    # PLACEHOLDER: Common ebook codes
    ebook_forms = {'EA', 'EB', 'EC', 'ED', 'EE', 'EF', 'EG', 'EH', 'EI', 'EJ', 'EK', 'EL'}
    ebook_details = {'E101', 'E102', 'E103', 'E104', 'E105', 'E116', 'E127', 'E139'}
    
    if product_form in ebook_forms:
        return True
        
    return any(detail in ebook_details for detail in form_details)

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