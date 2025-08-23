# MetaOps Validator - Tooltips Reference

This document catalogs all tooltips and help text throughout the MetaOps Validator interfaces to ensure consistent, helpful explanations for users.

## 🎯 Tooltip Design Principles

1. **Explain WHY, not just WHAT** - Focus on business impact and context
2. **Be concise but complete** - 1-2 sentences maximum  
3. **Use plain language** - Avoid technical jargon when possible
4. **Provide actionable guidance** - Include next steps when relevant
5. **Maintain consistency** - Use similar phrasing for similar concepts

## 📊 Nielsen Scoring Tooltips

### Main Metrics
- **Overall Score**: "Weighted completeness score. 50% is baseline, 75%+ is target for maximum sales impact"
- **Status**: "Quality assessment: Excellent (75%+) = maximum sales potential, Good (50-74%) = solid foundation, Needs Work (<50%) = significant gaps"  
- **Fields Scored**: "Weighted points earned vs total possible. Higher weights assigned to fields with greater sales impact"

### Field-Specific Explanations
- **ISBN**: "Unique product identifier - critical for discovery and sales tracking"
- **Title**: "Product title - primary discovery mechanism across all channels"
- **Contributors**: "Author/editor information - essential for reader identification and browsing"
- **Description**: "Product description - key factor in purchase decisions and SEO"
- **Subject Codes**: "BISAC/BIC subject classification - drives category placement and discovery"
- **Product Form**: "Physical format specification (book, ebook, audio) - affects distribution and pricing"
- **Price**: "Retail price information - required for buy button functionality"
- **Publication Date**: "Release date - impacts marketing, availability, and catalog organization"
- **Publisher**: "Publishing company - affects distribution relationships and brand recognition"
- **Imprint**: "Publishing imprint - additional brand/category information for specialized markets"
- **Series**: "Series information - drives discoverability for multi-book collections"
- **Cover Image**: "Product cover art - significantly impacts conversion rates in online retail"

## 🏪 Retailer Analysis Tooltips

### Summary Metrics
- **Average Score**: "Cross-retailer compatibility average. Higher scores indicate better acceptance likelihood across platforms"
- **Retailers Analyzed**: "Number of retailer profiles evaluated. Each has unique metadata requirements and weighting systems"
- **Best Fit**: "Retailer with highest compatibility score. Consider prioritizing this platform for distribution"
- **Needs Work**: "Retailer requiring most metadata improvements. Focus enhancement efforts here"

### Platform Contexts
- **Amazon**: "World's largest book retailer - prioritizes rich descriptions and subject codes for search"
- **IngramSpark**: "Major book distributor - requires publisher info and complete bibliographic data"
- **Apple Books**: "Premium digital platform - emphasizes quality descriptions and editorial content"
- **Kobo**: "Global ebook platform - focuses on discoverability and series information"
- **Barnes & Noble**: "Major US retailer - balances traditional and digital requirements"
- **OverDrive**: "Library platform - prioritizes cataloging data and institutional metadata"

## ⚙️ Validation Stage Tooltips

### Pipeline Stages
- **XSD Schema Validation**: "Validates XML structure against official ONIX 3.0 schema definitions. Ensures proper element hierarchy and data types."
- **Schematron Business Rules**: "Applies business logic validation using Schematron patterns. Checks publishing industry best practices and relationships."
- **Custom Rule Engine**: "Executes publisher-specific validation rules including contract compliance and territory restrictions."
- **Nielsen Completeness Scoring**: "Calculates metadata completeness score based on research correlating quality with sales performance (up to 75% uplift)."
- **Retailer Compatibility Analysis**: "Analyzes metadata against platform-specific requirements for Amazon, IngramSpark, Apple Books, and other major retailers."

### Validation Results
- **Errors**: "Critical issues that prevent processing or distribution. Must be fixed."
- **Warnings**: "Potential issues that may affect quality or compatibility. Should be reviewed."
- **Info**: "Informational messages and successful validation confirmations."

## 🔧 Quick Fix Tooltips

### Common Issues
- **ISBN Format**: "Ensure ISBN-13 format (13 digits) and use ProductIDType '15' for ISBN-13 or '03' for ISBN-10"
- **Required Elements**: "Review ONIX 3.0 schema requirements and ensure all mandatory child elements are present"
- **Namespace Issues**: "Add proper ONIX namespace declaration: xmlns='http://ns.editeur.org/onix/3.0/reference'"
- **Element Ordering**: "Check element ordering against ONIX schema - elements must appear in correct sequence"

## 📈 Dashboard Tooltips

### Batch Processing
- **Files Processed**: "Number of ONIX files successfully analyzed in this batch"
- **Avg Nielsen Score**: "Average metadata completeness score across all files. 75%+ indicates excellent quality."
- **Compliance Rate**: "Percentage of files passing validation without critical errors. 100% is the goal."
- **Total Issues**: "Combined count of errors and warnings across all processed files"

### Mode Selection
- **Mode Selection**: "Choose analysis mode: Single file for individual validation, Batch for multiple files with analytics, Historical for trend analysis"

## 🔄 File Upload Tooltips

- **Main Interface**: "Upload an ONIX 3.0 XML file for comprehensive validation and scoring. Supports both reference and short-tag variants."
- **Batch Upload**: "Select multiple ONIX XML files for batch processing"

## 📋 Interface Section Headers

### Main Headers with Context
- **Nielsen Completeness Score**: "Metadata completeness scoring based on research correlating quality with sales performance"
- **Retailer Compatibility Analysis**: "Platform-specific metadata requirements analysis for major book retailers"
- **XSD Schema Validation**: "Structural validation against ONIX 3.0 XML Schema Definition. Ensures proper XML structure and required elements."
- **Schematron Business Rules**: "Business logic validation using Schematron patterns. Checks relationships, constraints, and publishing industry rules."
- **Custom Rules Engine**: "Publisher-specific validation rules. Includes contract compliance, territory restrictions, and custom business logic."

## 💡 Implementation Notes

### Streamlit Tooltip Usage
```python
# Metrics with help text
st.metric("Score", "85%", help="Explanation text here")

# Headers with tooltips  
st.subheader("Section Title", help="Context explanation")

# Form elements with help
st.checkbox("Option", help="What this option does and why it matters")
```

### Tooltip Length Guidelines
- **Metric tooltips**: 50-80 characters
- **Section tooltips**: 80-120 characters  
- **Complex explanations**: 120-200 characters max
- **Field descriptions**: Focus on business impact, not technical details

### Consistency Patterns
- Start with action/purpose: "Validates...", "Calculates...", "Analyzes..."
- Include business context: "affects sales", "impacts discovery", "required for..."
- End with outcome: "ensures quality", "improves acceptance", "maximizes impact"

## 🎯 User Experience Goals

1. **Reduce Learning Curve**: New users understand validation concepts quickly
2. **Provide Context**: Explain why each metric/check matters for publishing success
3. **Guide Actions**: Help users prioritize improvements based on business impact
4. **Build Confidence**: Users understand what each score/result means for their metadata quality

This reference ensures all tooltips work together to create a cohesive, educational user experience that builds metadata expertise while solving immediate validation needs.