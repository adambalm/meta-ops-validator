# MetaOps Validator — ONIX Validation Platform

**Pre-feed ONIX validation and metadata completeness scoring for publishing success.**

Transform ONIX metadata quality with comprehensive validation, Nielsen completeness scoring, and retailer compatibility analysis. Designed for publishers, distributors, and metadata professionals.

## 🚀 Quick Access

**Live Demo:** [http://100.111.114.84:8507](http://100.111.114.84:8507) *(Main Validator)*

**Analytics Dashboard:** [http://100.111.114.84:8508](http://100.111.114.84:8508) *(Batch Processing)*

**Business Demo:** [http://100.111.114.84:8090](http://100.111.114.84:8090) *(Stakeholder View)*

## ✨ Key Features

### 🔍 Comprehensive Validation Pipeline
- **XSD Schema Validation** - Structural validation against ONIX 3.0 standards
- **Schematron Business Rules** - Publishing industry best practices
- **Custom Rule Engine** - Publisher-specific requirements and contracts
- **Nielsen Completeness Scoring** - Metadata quality correlation with sales performance
- **Retailer Compatibility Analysis** - Platform-specific requirements (Amazon, IngramSpark, Apple Books, etc.)

### 📊 Business Intelligence
- **Sales Impact Analysis** - Metadata completeness can drive up to 75% sales uplift
- **Retailer Readiness Scoring** - Platform compatibility assessment
- **Batch Processing Analytics** - Multi-file validation with trend analysis
- **Interactive Results** - Tabbed interface with detailed insights and quick fixes

### 🎯 User Experience
- **Contextual Help System** - Business-focused tooltips and guidance
- **Progressive Disclosure** - Information organized by complexity
- **Error Resolution Support** - Actionable quick fix suggestions
- **Export Capabilities** - CSV data and markdown reports

## 🏃‍♂️ Quickstart (5 Minutes)

### Option 1: Use Live Demo
Visit [http://100.111.114.84:8507](http://100.111.114.84:8507) - No setup required!

### Option 2: Local Installation
```bash
# Clone and setup
git clone https://github.com/user/meta-ops-validator.git
cd meta-ops-validator
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
export PYTHONPATH=$PWD/src

# Start main validator
streamlit run src/metaops/web/streamlit_app.py --server.port 8507 --server.address 0.0.0.0

# Or start analytics dashboard
streamlit run src/metaops/web/dashboard.py --server.port 8508 --server.address 0.0.0.0
```

### Option 3: CLI Usage
```bash
# Activate environment
source .venv/bin/activate
export PYTHONPATH=$PWD/src

# Validate ONIX file
python -m metaops.cli.main validate --file your_onix_file.xml

# Run specific validation stages
python -m metaops.cli.main validate-xsd --file your_onix_file.xml
python -m metaops.cli.main validate-schematron --file your_onix_file.xml
python -m metaops.cli.main run-rules --file your_onix_file.xml
```

## 📁 Test Files Included

The repository includes 15 generated ONIX test files with varying completeness levels:
- **Minimal** (30-40% completeness) - Basic required fields only
- **Basic** (50-60% completeness) - Standard publishing metadata
- **Good** (70-80% completeness) - Enhanced discovery metadata
- **Excellent** (90%+ completeness) - Maximum sales optimization
- **Problematic** - Intentional errors for testing validation rules

Files located in: `test_onix_files/`

## 🏗️ Architecture

### Validation Pipeline
1. **Namespace Detection** - Identifies ONIX reference vs. short-tag format
2. **XSD Validation** - Structural validation against ONIX 3.0 schema
3. **Schematron Rules** - Business logic and relationship validation
4. **Custom Rule Engine** - Publisher-specific validation rules
5. **Nielsen Scoring** - Completeness scoring with sales correlation
6. **Retailer Analysis** - Platform-specific compatibility assessment

### Web Interfaces
- **`streamlit_app.py`** - Main single-file validation interface
- **`dashboard.py`** - Analytics dashboard for batch processing
- **`streamlit_business_demo.py`** - Business stakeholder demonstrations

### Core Validators
- **`validators/onix_xsd.py`** - XSD schema validation
- **`validators/onix_schematron.py`** - Schematron business rules
- **`validators/nielsen_scoring.py`** - Completeness scoring engine
- **`validators/retailer_profiles.py`** - Multi-retailer compatibility
- **`rules/engine.py`** - Custom rule DSL processor

## 🧪 Testing

### UI Testing (Automated)
```bash
# Run UI usability tests with Playwright
python tests/test_ui_usability.py
```

### Core Function Testing
```bash
# Run validation pipeline tests
./test_core_functions.sh
```

### Generate Test Files
```bash
# Create ONIX test files with varying completeness
python scripts/generate_test_onix.py
```

## 📋 System Status

### Current Status ✅
- Complete validation pipeline operational  
- Mature web interfaces with comprehensive UX
- Nielsen completeness scoring with sales correlation
- Multi-retailer compatibility analysis
- Automated UI testing framework
- Comprehensive documentation and tooltips

### Schema Status ⚠️
- **Development**: Uses toy schemas for immediate functionality
- **Migration Path**: Ready for official EDItEUR ONIX 3.0 schemas
- **Migration**: See `data/editeur/README.md` for upgrade instructions

### Business Model Ready 💰
- Diagnostic report generation
- KPI tracking and analytics
- Multi-tier validation profiles
- Export capabilities for client deliverables

## 📖 Documentation

- **`TOOLTIPS_REFERENCE.md`** - Complete UI help text catalog
- **`UI_SPECIFICATION.md`** - Interface design and UX patterns
- **`TECHNICAL_SPECIFICATION.md`** - Architecture and integration details
- **`MVP_API_SPEC.md`** - RESTful API specification
- **`memory-bank/`** - Development context and patterns

## 🔧 Development

### Environment Setup
```bash
# Every development session
source .venv/bin/activate
export PYTHONPATH=/home/ed/meta-ops-validator/src
```

### Memory Bank Integration
This project uses Memory Bank MCP for persistent development context:
- **`memory-bank/active-context.md`** - Current development state
- **`memory-bank/progress.md`** - Task tracking and milestones
- **`memory-bank/decision-log.md`** - Architecture decisions with rationale

### Adding New Validators
1. Create validator in `src/metaops/validators/`
2. Add to pipeline in `CLAUDE.md` validation order
3. Update web interfaces with appropriate tooltips
4. Add test coverage in `tests/`

## 🤝 Contributing

1. Fork the repository
2. Follow the patterns in `memory-bank/system-patterns.md`
3. Ensure all validation stages maintain the pipeline order
4. Add appropriate tooltips with business context
5. Test UI changes with Playwright MCP
6. Update documentation and memory bank files

## 📜 License

See LICENSE file for details.

---

**MetaOps Validator** - Transforming ONIX metadata quality into publishing success.