# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

MetaOps Validator is a Pre-Feed ONIX validation system with CLI + GUI interfaces for enterprise publishing operations. It validates ONIX 3.x files using XSD, Schematron, and custom Rule DSL patterns, then generates operational KPI reports.

**Critical Context: The system uses official EDItEUR ONIX 3.0 schemas for enterprise validation.** All validation components are operational with real ONIX 3.x files using official EDItEUR schemas, automatic namespace detection, and full reference/short-tag support.

## Core Architecture

### Validation Pipeline
The system follows a five-stage validation approach:
1. **XSD Validation** (`src/metaops/validators/onix_xsd.py`) - Schema structure validation
2. **Schematron Rules** (`src/metaops/validators/onix_schematron.py`) - Business rule validation 
3. **Custom Rule DSL** (`src/metaops/rules/engine.py`) - Contract-aware validation using YAML rules with XPath expressions
4. **Nielsen Completeness Scoring** (`src/metaops/validators/nielsen_scoring.py`) - Metadata completeness correlation with sales performance
5. **Retailer Compatibility Analysis** (`src/metaops/validators/retailer_profiles.py`) - Platform-specific requirement validation

### Namespace Handling
The `src/metaops/onix_utils.py` module provides critical namespace detection:
- Distinguishes between toy format (no namespace) and real ONIX 3.x files
- Supports both ONIX reference tags (`http://ns.editeur.org/onix/3.0/reference`) and short tags (`http://ns.editeur.org/onix/3.0/short`)
- Issues warnings when toy schemas are used with real ONIX files

### Data Sources
- **Toy Data**: `data/samples/onix_samples/` - Demo files for development/testing
- **Production Migration**: `data/editeur/` - Directory for official EDItEUR schemas and codelists
- **Rules**: `diagnostic/` - Contains both toy and operational rule examples

### Output Formats
Validation results are output as structured data via reporters in `src/metaops/reporters/`:
- CSV/JSON for programmatic processing
- HTML summaries for human review
- All designed for KPI extraction (error rates, TTR proxies, incident counts)

## Development Commands

### Environment Setup
```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

### Running Components
```bash
# GUI Interface
streamlit run src/metaops/web/streamlit_app.py --server.port 8507 --server.address 0.0.0.0

# CLI Commands (requires PYTHONPATH)
export PYTHONPATH=/path/to/meta-ops-validator/src
python -m metaops.cli.main validate-xsd --onix data/samples/onix_samples/sample.xml --xsd data/samples/onix_samples/onix.xsd
python -m metaops.cli.main validate-schematron --onix data/samples/onix_samples/sample.xml --sch data/samples/onix_samples/rules.sch  
python -m metaops.cli.main run-rules --onix data/samples/onix_samples/sample.xml --rules diagnostic/rules.sample.yml
python -m metaops.cli.main report --in runs --out diagnostic/report.html
```

### Testing
```bash
# Run all tests
python -m pytest tests/

# Run specific test file
python -m pytest tests/test_onix_namespace_detection.py

# Run individual test
python -m pytest tests/test_onix_namespace_detection.py::TestNamespaceDetection::test_toy_onix_detection
```

### Using Make Targets
```bash
cd infra
make install    # Install dependencies
make gui        # Launch Streamlit GUI
make test       # Run tests
make demo       # Generate demo report
```

## Critical Implementation Details

### Toy vs Production Distinction
All validators and rule engines include safety checks to detect when toy schemas are used with real ONIX files. This prevents silent validation failures during the migration to production.

### XPath Namespace Awareness
The Rule DSL engine (`src/metaops/rules/engine.py`) detects ONIX namespace variants and adjusts XPath execution accordingly. Toy rules use simple paths like `//ProductForm`, while production rules must use namespace-aware paths like `//onix:DescriptiveDetail/onix:ProductForm`.

### Codelist Integration Framework
`src/metaops/codelists.py` provides the foundation for loading official EDItEUR codelists. Current implementations are placeholders - real production use requires downloading and integrating official codelist files into `data/editeur/codelists/`.

### GUI Safety Guards
The Streamlit interfaces include comprehensive tooltip systems and namespace detection warnings:
- **Main Validator** (`src/metaops/web/streamlit_app.py`) - Single file validation with contextual help
- **Analytics Dashboard** (`src/metaops/web/dashboard.py`) - Batch processing and analytics
- **Business Demo** (`src/metaops/web/streamlit_business_demo.py`) - Stakeholder demonstrations

## Production Migration Path

The system is designed for a specific migration sequence:

1. **Place Official Artifacts**: Download EDItEUR schemas and codelists into `data/editeur/` per instructions in that directory's README
2. **Update Validators**: Point XSD/Schematron validators to use official schemas instead of toy versions  
3. **Retrofit XPaths**: Update all Rule DSL examples to use namespace-aware XPaths
4. **Enable Codelists**: Load official codelists in `codelists.py` for semantic validation
5. **Test Migration**: Use regression tests in `tests/test_onix_namespace_detection.py` to verify toy→production transition

The codebase includes extensive comments marking toy vs production code sections, and template files showing the target production structure with proper ONIX namespaces and composite handling.