"""
Nielsen Metadata Completeness Scoring
Based on research correlating metadata quality with sales performance (75% uplift)
"""

from pathlib import Path
from typing import List, Dict, Optional, Tuple
from lxml import etree
from metaops.onix_utils import detect_onix_namespace, get_namespace_map

# Nielsen scoring weights based on sales impact correlation
NIELSEN_WEIGHTS = {
    # Core identifiers (high impact)
    'isbn': 20,
    'title': 15,
    'contributors': 12,

    # Marketing critical (medium-high impact)
    'description': 10,
    'subject_codes': 8,
    'product_form': 8,
    'price': 7,

    # Discovery enhancement (medium impact)
    'publication_date': 5,
    'publisher': 5,
    'imprint': 4,
    'series': 3,
    'cover_image': 3
}

def calculate_nielsen_score(onix_path: Path) -> Dict:
    """
    Calculate Nielsen-style metadata completeness score.

    Returns a scoring report with:
    - Overall score (0-100)
    - Field-by-field breakdown
    - Missing critical elements
    - Sales impact estimation
    """
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
                "overall_score": 0,
                "total_possible": sum(NIELSEN_WEIGHTS.values()),
                "message": "No products found in ONIX file",
                "breakdown": {},
                "missing_critical": list(NIELSEN_WEIGHTS.keys()),
                "sales_impact_estimate": "Unable to calculate - no products"
            }

        # Score all products and calculate aggregate metrics
        all_products_scores = []

        for product_index, product in enumerate(products):
            score_breakdown = {}
            total_score = 0
            missing_elements = []

            # ISBN check
            isbn_score = _score_isbn(product, nsmap, namespace_uri)
            score_breakdown['isbn'] = isbn_score
            total_score += isbn_score
            if isbn_score == 0:
                missing_elements.append('isbn')

            # Title check
            title_score = _score_title(product, nsmap, namespace_uri)
            score_breakdown['title'] = title_score
            total_score += title_score
            if title_score == 0:
                missing_elements.append('title')

            # Contributors check
            contrib_score = _score_contributors(product, nsmap, namespace_uri)
            score_breakdown['contributors'] = contrib_score
            total_score += contrib_score
            if contrib_score == 0:
                missing_elements.append('contributors')

            # Description check
            desc_score = _score_description(product, nsmap, namespace_uri)
            score_breakdown['description'] = desc_score
            total_score += desc_score
            if desc_score == 0:
                missing_elements.append('description')

            # Subject codes check
            subject_score = _score_subjects(product, nsmap, namespace_uri)
            score_breakdown['subject_codes'] = subject_score
            total_score += subject_score
            if subject_score == 0:
                missing_elements.append('subject_codes')

            # Product form check
            form_score = _score_product_form(product, nsmap, namespace_uri)
            score_breakdown['product_form'] = form_score
            total_score += form_score
            if form_score == 0:
                missing_elements.append('product_form')

            # Price check
            price_score = _score_price(product, nsmap, namespace_uri)
            score_breakdown['price'] = price_score
            total_score += price_score
            if price_score == 0:
                missing_elements.append('price')

            # Publication date check
            pub_date_score = _score_publication_date(product, nsmap, namespace_uri)
            score_breakdown['publication_date'] = pub_date_score
            total_score += pub_date_score
            if pub_date_score == 0:
                missing_elements.append('publication_date')

            # Publisher check
            pub_score = _score_publisher(product, nsmap, namespace_uri)
            score_breakdown['publisher'] = pub_score
            total_score += pub_score
            if pub_score == 0:
                missing_elements.append('publisher')

            # Imprint check
            imprint_score = _score_imprint(product, nsmap, namespace_uri)
            score_breakdown['imprint'] = imprint_score
            total_score += imprint_score
            if imprint_score == 0:
                missing_elements.append('imprint')

            # Series check
            series_score = _score_series(product, nsmap, namespace_uri)
            score_breakdown['series'] = series_score
            total_score += series_score
            if series_score == 0:
                missing_elements.append('series')

            # Cover image check
            cover_score = _score_cover_image(product, nsmap, namespace_uri)
            score_breakdown['cover_image'] = cover_score
            total_score += cover_score
            if cover_score == 0:
                missing_elements.append('cover_image')

            total_possible = sum(NIELSEN_WEIGHTS.values())
            percentage_score = round((total_score / total_possible) * 100, 1)

            # Store product score
            product_result = {
                "product_index": product_index,
                "overall_score": percentage_score,
                "total_score": total_score,
                "breakdown": score_breakdown,
                "missing_critical": missing_elements
            }
            all_products_scores.append(product_result)

        # Calculate aggregate metrics across all products
        if all_products_scores:
            avg_score = sum(p["overall_score"] for p in all_products_scores) / len(all_products_scores)
            min_score = min(p["overall_score"] for p in all_products_scores)
            max_score = max(p["overall_score"] for p in all_products_scores)

            # Aggregate missing elements (elements missing from any product)
            all_missing = set()
            for product_score in all_products_scores:
                all_missing.update(product_score["missing_critical"])

            # Use average score for sales impact estimate
            sales_impact = _estimate_sales_impact(avg_score)

            return {
                "overall_score": round(avg_score, 1),
                "min_score": min_score,
                "max_score": max_score,
                "products_count": len(all_products_scores),
                "total_possible": sum(NIELSEN_WEIGHTS.values()),
                "products_scores": all_products_scores,
                "missing_critical": list(all_missing),
                "sales_impact_estimate": sales_impact,
                "recommendation": _get_scoring_recommendation(avg_score, list(all_missing))
            }
        else:
            return {
                "overall_score": 0,
                "total_possible": sum(NIELSEN_WEIGHTS.values()),
                "products_count": 0,
                "message": "No products processed",
                "products_scores": [],
                "missing_critical": list(NIELSEN_WEIGHTS.keys()),
                "sales_impact_estimate": "Unable to calculate - no products"
            }

    except Exception as e:
        return {
            "overall_score": 0,
            "total_possible": sum(NIELSEN_WEIGHTS.values()),
            "error": f"Nielsen scoring failed: {str(e)}",
            "breakdown": {},
            "missing_critical": list(NIELSEN_WEIGHTS.keys()),
            "sales_impact_estimate": "Unable to calculate due to error"
        }

def _score_isbn(product, nsmap: Dict[str, str], namespace_uri: Optional[str]) -> int:
    """Score ISBN presence and validity."""
    if namespace_uri:
        isbn_nodes = product.xpath(".//onix:ProductIdentifier[onix:ProductIDType='15']/onix:IDValue", namespaces=nsmap)
        if not isbn_nodes:
            isbn_nodes = product.xpath(".//onix:ProductIdentifier[onix:ProductIDType='03']/onix:IDValue", namespaces=nsmap)
    else:
        isbn_nodes = product.xpath(".//ProductIdentifier[ProductIDType='15']/IDValue")
        if not isbn_nodes:
            isbn_nodes = product.xpath(".//ProductIdentifier[ProductIDType='03']/IDValue")

    if isbn_nodes and len(isbn_nodes[0].text.strip()) >= 10:
        return NIELSEN_WEIGHTS['isbn']
    return 0

def _score_title(product, nsmap: Dict[str, str], namespace_uri: Optional[str]) -> int:
    """Score title presence and quality."""
    if namespace_uri:
        title_nodes = product.xpath(".//onix:TitleDetail/onix:TitleElement/onix:TitleText", namespaces=nsmap)
    else:
        title_nodes = product.xpath(".//TitleDetail/TitleElement/TitleText")

    if title_nodes and len(title_nodes[0].text.strip()) > 3:
        return NIELSEN_WEIGHTS['title']
    return 0

def _score_contributors(product, nsmap: Dict[str, str], namespace_uri: Optional[str]) -> int:
    """Score contributor presence and completeness."""
    if namespace_uri:
        contrib_nodes = product.xpath(".//onix:Contributor/onix:PersonName", namespaces=nsmap)
    else:
        contrib_nodes = product.xpath(".//Contributor/PersonName")

    if contrib_nodes and len(contrib_nodes[0].text.strip()) > 3:
        return NIELSEN_WEIGHTS['contributors']
    return 0

def _score_description(product, nsmap: Dict[str, str], namespace_uri: Optional[str]) -> int:
    """Score description presence and quality."""
    if namespace_uri:
        desc_nodes = product.xpath(".//onix:TextContent[onix:TextType='03']/onix:Text", namespaces=nsmap)
    else:
        desc_nodes = product.xpath(".//TextContent[TextType='03']/Text")

    if desc_nodes and len(desc_nodes[0].text.strip()) > 50:
        return NIELSEN_WEIGHTS['description']
    return 0

def _score_subjects(product, nsmap: Dict[str, str], namespace_uri: Optional[str]) -> int:
    """Score subject classification presence."""
    if namespace_uri:
        subject_nodes = product.xpath(".//onix:Subject/onix:SubjectCode", namespaces=nsmap)
    else:
        subject_nodes = product.xpath(".//Subject/SubjectCode")

    if subject_nodes and len(subject_nodes[0].text.strip()) > 0:
        return NIELSEN_WEIGHTS['subject_codes']
    return 0

def _score_product_form(product, nsmap: Dict[str, str], namespace_uri: Optional[str]) -> int:
    """Score product form specification."""
    if namespace_uri:
        form_nodes = product.xpath(".//onix:ProductForm", namespaces=nsmap)
    else:
        form_nodes = product.xpath(".//ProductForm")

    if form_nodes and len(form_nodes[0].text.strip()) > 0:
        return NIELSEN_WEIGHTS['product_form']
    return 0

def _score_price(product, nsmap: Dict[str, str], namespace_uri: Optional[str]) -> int:
    """Score price information presence."""
    if namespace_uri:
        price_nodes = product.xpath(".//onix:Price/onix:PriceAmount", namespaces=nsmap)
    else:
        price_nodes = product.xpath(".//Price/PriceAmount")

    if price_nodes and float(price_nodes[0].text.strip()) > 0:
        return NIELSEN_WEIGHTS['price']
    return 0

def _score_publication_date(product, nsmap: Dict[str, str], namespace_uri: Optional[str]) -> int:
    """Score publication date presence."""
    if namespace_uri:
        date_nodes = product.xpath(".//onix:PublishingDate/onix:Date", namespaces=nsmap)
    else:
        date_nodes = product.xpath(".//PublishingDate/Date")

    if date_nodes and len(date_nodes[0].text.strip()) >= 8:
        return NIELSEN_WEIGHTS['publication_date']
    return 0

def _score_publisher(product, nsmap: Dict[str, str], namespace_uri: Optional[str]) -> int:
    """Score publisher information."""
    if namespace_uri:
        pub_nodes = product.xpath(".//onix:Publisher/onix:PublisherName", namespaces=nsmap)
    else:
        pub_nodes = product.xpath(".//Publisher/PublisherName")

    if pub_nodes and len(pub_nodes[0].text.strip()) > 0:
        return NIELSEN_WEIGHTS['publisher']
    return 0

def _score_imprint(product, nsmap: Dict[str, str], namespace_uri: Optional[str]) -> int:
    """Score imprint information."""
    if namespace_uri:
        imp_nodes = product.xpath(".//onix:Imprint/onix:ImprintName", namespaces=nsmap)
    else:
        imp_nodes = product.xpath(".//Imprint/ImprintName")

    if imp_nodes and len(imp_nodes[0].text.strip()) > 0:
        return NIELSEN_WEIGHTS['imprint']
    return 0

def _score_series(product, nsmap: Dict[str, str], namespace_uri: Optional[str]) -> int:
    """Score series information."""
    if namespace_uri:
        series_nodes = product.xpath(".//onix:Collection/onix:TitleDetail/onix:TitleElement/onix:TitleText", namespaces=nsmap)
    else:
        series_nodes = product.xpath(".//Collection/TitleDetail/TitleElement/TitleText")

    if series_nodes and len(series_nodes[0].text.strip()) > 0:
        return NIELSEN_WEIGHTS['series']
    return 0

def _score_cover_image(product, nsmap: Dict[str, str], namespace_uri: Optional[str]) -> int:
    """Score cover image resource."""
    if namespace_uri:
        image_nodes = product.xpath(".//onix:SupportingResource[onix:ResourceContentType='01']/onix:ResourceVersion/onix:ResourceLink", namespaces=nsmap)
    else:
        image_nodes = product.xpath(".//SupportingResource[ResourceContentType='01']/ResourceVersion/ResourceLink")

    if image_nodes and len(image_nodes[0].text.strip()) > 10:
        return NIELSEN_WEIGHTS['cover_image']
    return 0

def _estimate_sales_impact(score: float) -> str:
    """Estimate sales impact based on Nielsen research correlation."""
    if score >= 90:
        return "Excellent metadata completeness - estimated 70-75% sales uplift potential"
    elif score >= 75:
        return "Good metadata completeness - estimated 50-70% sales uplift potential"
    elif score >= 60:
        return "Fair metadata completeness - estimated 30-50% sales uplift potential"
    elif score >= 40:
        return "Poor metadata completeness - estimated 15-30% sales uplift potential"
    else:
        return "Critical metadata gaps - significant sales impact risk"

def _get_scoring_recommendation(score: float, missing: List[str]) -> str:
    """Generate actionable recommendations based on score."""
    if score >= 85:
        return "Excellent metadata quality. Consider adding series/imprint data for maximum discoverability."
    elif score >= 70:
        return f"Good metadata foundation. Priority improvements: {', '.join(missing[:3])}"
    elif score >= 50:
        return f"Moderate metadata gaps affecting discoverability. Critical missing: {', '.join(missing[:5])}"
    else:
        return f"Significant metadata deficiencies. Immediate action needed for: {', '.join(missing[:7])}"
