"""
Retailer-Specific Metadata Completeness Profiles
Based on individual retailer requirements and discovery algorithms
"""

from typing import Dict, List, Optional
from pathlib import Path
from lxml import etree
from metaops.onix_utils import detect_onix_namespace, get_namespace_map

# Retailer-specific metadata requirements
RETAILER_PROFILES = {
    'amazon': {
        'name': 'Amazon KDP/Author Central',
        'critical_fields': ['isbn', 'title', 'contributors', 'description', 'product_form', 'price'],
        'recommended_fields': ['subject_codes', 'series', 'cover_image', 'publication_date'],
        'weights': {
            'isbn': 25, 'title': 20, 'contributors': 15, 'description': 15, 
            'product_form': 10, 'price': 10, 'subject_codes': 3, 'series': 2
        },
        'discovery_boost': ['subject_codes', 'series', 'description'],
        'buy_button_requirements': ['isbn', 'price', 'product_form']
    },
    'ingram': {
        'name': 'IngramSpark',
        'critical_fields': ['isbn', 'title', 'contributors', 'product_form', 'price', 'publisher'],
        'recommended_fields': ['description', 'subject_codes', 'publication_date', 'imprint'],
        'weights': {
            'isbn': 20, 'title': 18, 'contributors': 15, 'product_form': 12,
            'price': 12, 'publisher': 10, 'description': 8, 'subject_codes': 5
        },
        'discovery_boost': ['subject_codes', 'publisher', 'imprint'],
        'distribution_requirements': ['isbn', 'publisher', 'price']
    },
    'apple': {
        'name': 'Apple Books',
        'critical_fields': ['isbn', 'title', 'contributors', 'description', 'product_form'],
        'recommended_fields': ['subject_codes', 'series', 'cover_image', 'price'],
        'weights': {
            'isbn': 22, 'title': 20, 'contributors': 18, 'description': 15,
            'product_form': 12, 'subject_codes': 8, 'series': 3, 'cover_image': 2
        },
        'discovery_boost': ['description', 'subject_codes', 'series'],
        'editorial_requirements': ['description', 'cover_image']
    },
    'kobo': {
        'name': 'Kobo',
        'critical_fields': ['isbn', 'title', 'contributors', 'description', 'product_form', 'price'],
        'recommended_fields': ['subject_codes', 'series', 'publication_date'],
        'weights': {
            'isbn': 20, 'title': 18, 'contributors': 16, 'description': 14,
            'product_form': 12, 'price': 10, 'subject_codes': 6, 'series': 4
        },
        'discovery_boost': ['description', 'subject_codes', 'series'],
        'merchandising_requirements': ['description', 'series']
    },
    'barnes_noble': {
        'name': 'Barnes & Noble Press',
        'critical_fields': ['isbn', 'title', 'contributors', 'description', 'product_form', 'price'],
        'recommended_fields': ['subject_codes', 'publisher', 'series', 'cover_image'],
        'weights': {
            'isbn': 22, 'title': 18, 'contributors': 15, 'description': 15,
            'product_form': 12, 'price': 8, 'subject_codes': 6, 'publisher': 4
        },
        'discovery_boost': ['description', 'subject_codes', 'publisher'],
        'store_requirements': ['title', 'contributors', 'description']
    },
    'overdrive': {
        'name': 'OverDrive',
        'critical_fields': ['isbn', 'title', 'contributors', 'description', 'product_form', 'publisher'],
        'recommended_fields': ['subject_codes', 'series', 'publication_date', 'imprint'],
        'weights': {
            'isbn': 18, 'title': 16, 'contributors': 14, 'description': 12,
            'product_form': 12, 'publisher': 12, 'subject_codes': 8, 'series': 8
        },
        'discovery_boost': ['subject_codes', 'series', 'publisher'],
        'library_requirements': ['publisher', 'subject_codes', 'description']
    }
}

def calculate_retailer_score(onix_path: Path, retailer: str) -> Dict:
    """
    Calculate retailer-specific metadata completeness score.
    
    Args:
        onix_path: Path to ONIX file
        retailer: Retailer profile key (amazon, ingram, etc.)
    
    Returns:
        Dict with retailer-specific scoring results
    """
    if retailer not in RETAILER_PROFILES:
        return {
            "error": f"Unknown retailer profile: {retailer}",
            "available_profiles": list(RETAILER_PROFILES.keys())
        }
    
    profile = RETAILER_PROFILES[retailer]
    namespace_uri, is_real_onix = detect_onix_namespace(onix_path)
    nsmap = get_namespace_map(namespace_uri)
    
    try:
        xml_doc = etree.parse(str(onix_path))
        root = xml_doc.getroot()
        
        # Find product nodes
        if namespace_uri:
            products = root.xpath("//onix:Product", namespaces=nsmap)
        else:
            products = root.xpath("//Product")
        
        if not products:
            return {
                "retailer": profile['name'],
                "overall_score": 0,
                "message": "No products found in ONIX file",
                "critical_missing": profile['critical_fields'],
                "risk_level": "HIGH"
            }
        
        # Score first product
        product = products[0]
        field_scores = {}
        total_score = 0
        missing_critical = []
        missing_recommended = []
        
        # Score each field in the retailer's weight system
        for field, weight in profile['weights'].items():
            score = _score_field_for_retailer(product, field, nsmap, namespace_uri)
            field_scores[field] = {
                'score': score,
                'weight': weight,
                'weighted_score': score * (weight / 100) if score > 0 else 0
            }
            
            if score > 0:
                total_score += field_scores[field]['weighted_score']
            else:
                if field in profile['critical_fields']:
                    missing_critical.append(field)
                elif field in profile['recommended_fields']:
                    missing_recommended.append(field)
        
        # Calculate additional insights
        discovery_score = _calculate_discovery_score(field_scores, profile['discovery_boost'])
        risk_assessment = _assess_retailer_risk(missing_critical, profile)
        recommendations = _generate_retailer_recommendations(missing_critical, missing_recommended, profile)
        
        return {
            "retailer": profile['name'],
            "retailer_key": retailer,
            "overall_score": round(total_score, 1),
            "max_possible": 100,
            "field_breakdown": field_scores,
            "critical_missing": missing_critical,
            "recommended_missing": missing_recommended,
            "discovery_score": discovery_score,
            "risk_level": risk_assessment['level'],
            "risk_factors": risk_assessment['factors'],
            "recommendations": recommendations,
            "compliance_status": _get_compliance_status(missing_critical, profile)
        }
        
    except Exception as e:
        return {
            "retailer": profile['name'],
            "error": f"Retailer scoring failed: {str(e)}",
            "overall_score": 0,
            "risk_level": "UNKNOWN"
        }

def calculate_multi_retailer_score(onix_path: Path, retailers: Optional[List[str]] = None) -> Dict:
    """
    Calculate scores for multiple retailers and provide comparative analysis.
    """
    if retailers is None:
        retailers = list(RETAILER_PROFILES.keys())
    
    retailer_scores = {}
    
    for retailer in retailers:
        if retailer in RETAILER_PROFILES:
            retailer_scores[retailer] = calculate_retailer_score(onix_path, retailer)
    
    if not retailer_scores:
        return {"error": "No valid retailer profiles provided"}
    
    # Calculate comparative metrics
    scores = [(k, v.get('overall_score', 0)) for k, v in retailer_scores.items() if 'overall_score' in v]
    
    if scores:
        avg_score = sum(score for _, score in scores) / len(scores)
        best_fit = max(scores, key=lambda x: x[1])
        worst_fit = min(scores, key=lambda x: x[1])
        
        # Find common missing fields across retailers  
        all_missing = []
        for retailer_data in retailer_scores.values():
            if 'critical_missing' in retailer_data:
                all_missing.extend(retailer_data['critical_missing'])
        
        common_gaps = list(set(field for field in all_missing if all_missing.count(field) >= len(retailers) // 2))
        
        return {
            "file": onix_path.name,
            "retailers_analyzed": len(retailer_scores),
            "average_score": round(avg_score, 1),
            "best_fit_retailer": best_fit[0],
            "best_fit_score": best_fit[1],
            "worst_fit_retailer": worst_fit[0],
            "worst_fit_score": worst_fit[1],
            "common_gaps": common_gaps,
            "retailer_details": retailer_scores,
            "recommendation": _generate_multi_retailer_recommendation(retailer_scores, common_gaps)
        }
    
    return {"error": "Unable to calculate comparative metrics", "retailer_details": retailer_scores}

def _score_field_for_retailer(product, field: str, nsmap: Dict[str, str], namespace_uri: Optional[str]) -> int:
    """Score individual fields using the same logic as Nielsen scoring."""
    # Reuse the field scoring logic from nielsen_scoring.py
    from metaops.validators.nielsen_scoring import (
        _score_isbn, _score_title, _score_contributors, _score_description,
        _score_subjects, _score_product_form, _score_price, _score_publication_date,
        _score_publisher, _score_imprint, _score_series, _score_cover_image
    )
    
    field_scorers = {
        'isbn': _score_isbn,
        'title': _score_title,
        'contributors': _score_contributors,
        'description': _score_description,
        'subject_codes': _score_subjects,
        'product_form': _score_product_form,
        'price': _score_price,
        'publication_date': _score_publication_date,
        'publisher': _score_publisher,
        'imprint': _score_imprint,
        'series': _score_series,
        'cover_image': _score_cover_image
    }
    
    if field in field_scorers:
        score = field_scorers[field](product, nsmap, namespace_uri)
        return 100 if score > 0 else 0  # Binary scoring for retailer profiles
    
    return 0

def _calculate_discovery_score(field_scores: Dict, discovery_fields: List[str]) -> float:
    """Calculate discovery optimization score based on retailer's algorithm preferences."""
    discovery_total = 0
    discovery_possible = 0
    
    for field in discovery_fields:
        if field in field_scores:
            discovery_total += field_scores[field]['weighted_score']
            discovery_possible += field_scores[field]['weight']
    
    return round((discovery_total / discovery_possible * 100) if discovery_possible > 0 else 0, 1)

def _assess_retailer_risk(missing_critical: List[str], profile: Dict) -> Dict:
    """Assess risk level for specific retailer based on missing critical fields."""
    critical_count = len(missing_critical)
    total_critical = len(profile['critical_fields'])
    
    if critical_count == 0:
        return {"level": "LOW", "factors": ["All critical fields present"]}
    elif critical_count <= total_critical * 0.3:
        return {"level": "MEDIUM", "factors": [f"Missing {critical_count} critical fields", "May affect discoverability"]}
    else:
        factors = [f"Missing {critical_count} critical fields", "High rejection risk"]
        
        # Check for buy button / distribution risks
        if any(field in missing_critical for field in ['isbn', 'price', 'product_form']):
            factors.append("Buy button functionality at risk")
        
        return {"level": "HIGH", "factors": factors}

def _generate_retailer_recommendations(critical_missing: List[str], recommended_missing: List[str], profile: Dict) -> List[str]:
    """Generate actionable recommendations for retailer compliance."""
    recommendations = []
    
    if critical_missing:
        recommendations.append(f"CRITICAL: Add missing required fields: {', '.join(critical_missing[:5])}")
    
    if recommended_missing:
        recommendations.append(f"OPTIMIZE: Add recommended fields for better discovery: {', '.join(recommended_missing[:3])}")
    
    # Retailer-specific advice
    retailer_name = profile['name']
    if 'amazon' in retailer_name.lower() and 'description' in critical_missing:
        recommendations.append("Amazon requires rich descriptions for search ranking")
    
    if 'ingram' in retailer_name.lower() and 'publisher' in critical_missing:
        recommendations.append("IngramSpark requires publisher info for distribution")
    
    if not recommendations:
        recommendations.append(f"Excellent! Meets all {retailer_name} requirements")
    
    return recommendations

def _get_compliance_status(missing_critical: List[str], profile: Dict) -> str:
    """Determine compliance status for retailer requirements."""
    if not missing_critical:
        return "COMPLIANT"
    elif len(missing_critical) <= 2:
        return "PARTIAL_COMPLIANCE"
    else:
        return "NON_COMPLIANT"

def _generate_multi_retailer_recommendation(retailer_scores: Dict, common_gaps: List[str]) -> str:
    """Generate recommendation based on multi-retailer analysis."""
    if not common_gaps:
        return "Good cross-retailer compatibility. Consider optimizing for your primary sales channels."
    
    return f"Priority: Fix common gaps across retailers: {', '.join(common_gaps[:5])}. This will improve acceptance rates across all platforms."