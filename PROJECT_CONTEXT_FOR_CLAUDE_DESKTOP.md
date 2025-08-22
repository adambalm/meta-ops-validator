# MetaOps Validator - Project Context for Claude Desktop

*Generated for Claude Desktop workflow optimization - Contains complete project context*

## Project Overview

**MetaOps Validator** is a Pre-Feed ONIX validation system with CLI + GUI interfaces targeting enterprise publishing operations. It validates ONIX 3.x files using XSD, Schematron, and custom Rule DSL patterns, then generates operational KPI reports.

**Business Model:** $4,950 5-day diagnostic service → $7.5-10K/month 3-month contracts with enterprise publishers (starting with Simon & Schuster outreach).

**Current Status:** Demo-ready with toy schemas, needs migration to production EDItEUR schemas.

## Tech Stack & Architecture

### Core Components
```
src/metaops/
├── cli/main.py                    # Typer CLI interface
├── validators/
│   ├── onix_xsd.py               # XML Schema validation
│   ├── onix_schematron.py        # Business rule validation  
│   └── presence.py               # Presence scoring
├── rules/
│   ├── engine.py                 # Custom YAML rule DSL
│   └── dsl.py                    # Rule parsing
├── reporters/                     # JSON/CSV/HTML output
├── onix_utils.py                 # Namespace detection
└── codelists.py                  # EDItEUR codelist integration
```

### Tech Dependencies
- **Python 3.12** with pytest testing
- **lxml** for XML processing
- **Typer** for CLI interface  
- **Streamlit** for GUI dashboard
- **Jinja2** for report templating
- **pandas** for data processing

### Data Architecture
```
data/
├── samples/onix_samples/         # Toy demo files (current)
│   ├── sample.xml               # Demo ONIX file
│   ├── onix.xsd                 # Toy XSD schema
│   └── rules.sch                # Demo Schematron
└── editeur/                     # Production schemas (future)
    └── README.md                # Migration instructions
```

## Three-Context Claude Architecture

The project uses a **multi-context Claude architecture** based on work focus:

### 1. CLAUDE_TECHNICAL.md
**When:** Building/modifying validation engines, parsers, tests
- Core validation pipeline (XSD → Schematron → Rule DSL)
- Namespace detection and compatibility warnings
- PYTHONPATH setup: `export PYTHONPATH=/path/to/meta-ops-validator/src`
- Test execution: `python -m pytest tests/`

### 2. CLAUDE_BUSINESS.md  
**When:** Creating client deliverables, demos, sales materials
- **Visual Identity:** Pure Tufte CSS (no chartjunk, data-forward)
- **Data Ethics:** No scraping, API/docs-first, [verified] vs [inference] tags
- **ONIX Compliance:** All examples must be properly namespaced
- **Deliverable Structure:** Reports → Dashboards → Sales toolkit

### 3. CLAUDE_INTEGRATION.md (Future)
**When:** Connecting business dashboard to validator, data pipelines

## Current Pain Points & Context Loss Issues

### 1. Environment Setup Inconsistency
**Problem:** Claude often runs Python commands without activating `.venv` despite clear documentation stating `source .venv/bin/activate`

**Current Workaround:** Created `test_core_functions.sh` that enforces environment

**Need:** Systematic way to ensure environment setup is automatic

### 2. Context File Selection
**Problem:** Claude doesn't consistently choose the right context file (TECHNICAL vs BUSINESS) based on task

**Current State:** Manual specification required ("use CLAUDE_TECHNICAL.md")

**Need:** Better task-to-context routing

### 3. Toy vs Production Schema Awareness
**Problem:** System uses toy schemas but must warn when used with real ONIX files

**Current Implementation:** Namespace detection in `src/metaops/onix_utils.py`

**Critical Rule:** ALL ONIX examples in client-facing materials MUST use proper namespaces:
```xml
<!-- CORRECT -->
<onix:Product xmlns:onix="http://ns.editeur.org/onix/3.0/reference">

<!-- WRONG -->
<Product>
```

### 4. Testing Workflow Friction
**Problem:** Multi-step setup for running tests (venv + PYTHONPATH + pytest)

**Current Solution:** `./test_core_functions.sh` script

**Baseline Status:** 8 passing tests, 3 skipped (migration readiness)

## Established Workflows & Conventions

### Development Commands
```bash
# Environment setup (ALWAYS required)
source .venv/bin/activate
export PYTHONPATH=/home/ed/meta-ops-validator/src

# Core testing
./test_core_functions.sh              # Complete test suite
python -m pytest tests/ -v           # Python tests only

# CLI validation
python -m metaops.cli.main validate-xsd --onix data/samples/onix_samples/sample.xml --xsd data/samples/onix_samples/onix.xsd
python -m metaops.cli.main validate-schematron --onix data/samples/onix_samples/sample.xml --sch data/samples/onix_samples/rules.sch
python -m metaops.cli.main run-rules --onix data/samples/onix_samples/sample.xml --rules diagnostic/rules.sample.yml

# GUI
streamlit run streamlit_app.py        # Available at http://localhost:8501
```

### Git Workflow
- Commit format: `type: description` with Claude attribution
- Current branch: `main`
- Recent baseline commit: `1650e72` (test harness addition)

### Code Conventions
- **Never create files unless absolutely necessary**
- **Always prefer editing existing files**  
- **No documentation files unless explicitly requested**
- **Follow existing code patterns and imports**

## Critical Business Context

### Target: Simon & Schuster Outreach
- **Timeline:** Demo ready by Aug 31, 2025
- **Positioning:** Pre-feed validator complement to Firebrand/Eloquence
- **Buyer:** Publishing Operations teams with deep ONIX knowledge

### Data Compliance Requirements
```yaml
ALLOWED_DATA:
  - EDItEUR official samples
  - Public catalog pages (simonandschuster.com)
  - Amazon/B&N public APIs
  - Library catalogs with public ONIX
  - SEC filings with contract examples

FORBIDDEN:
  - Retailer scraping beyond public APIs
  - Client data without permission
  - Fake ISBNs that could collide
```

### Visual Requirements
- **Tufte CSS foundation** for all client materials
- **Data-ink ratio maximization**
- **No chartjunk** (3D, gradients, animations)
- **Tables over charts** for precision
- **Evidence tagging:** [verified] vs [inference] on all metrics

## Current Deliverable Gap

**What Exists:**
- ✅ Technical validator (toy schemas)
- ✅ CLI + GUI interfaces  
- ✅ Test suite (baseline)
- ✅ Namespace detection

**What's Missing (per CLAUDE_BUSINESS.md):**
- ❌ `presentation/` layer (reports, dashboard)
- ❌ `toolkit/` sales materials
- ❌ `artifacts/` client deliverables
- ❌ S&S public data integration
- ❌ Tufte-styled demo dashboard

## Production Migration Requirements

**Critical Path:**
1. Replace toy XSD with EDItEUR ONIX 3.x schema
2. Load official EDItEUR codelists  
3. Update all XPaths to namespace-aware
4. Test against real ONIX 3.x files
5. Replace toy Schematron with publisher rules

**Migration Guide:** `data/editeur/README.md`

## Specific Claude Desktop Optimization Needs

### 1. Automatic Environment Detection
Need workflow that auto-activates `.venv` and sets PYTHONPATH when working in this project

### 2. Context-Aware Task Routing
Need system to automatically use CLAUDE_TECHNICAL.md for code tasks, CLAUDE_BUSINESS.md for deliverables

### 3. Validation Pipeline Memory
Need to remember:
- Current validation results format
- Namespace detection patterns  
- Report template structure
- Client data compliance rules

### 4. Demo Readiness Tracking
Need to track progress toward S&S demo:
- [ ] Public S&S catalog integration
- [ ] Tufte dashboard implementation
- [ ] Sales toolkit creation
- [ ] Diagnostic report templates

## File Structure Reference
```
meta-ops-validator/
├── CLAUDE.md                    # Context routing guide
├── CLAUDE_TECHNICAL.md          # Dev context
├── CLAUDE_BUSINESS.md           # Client context  
├── README.md                    # Project overview
├── requirements.txt             # Dependencies
├── streamlit_app.py            # GUI interface
├── test_core_functions.sh      # Test harness
├── src/metaops/               # Core validation engine
├── tests/                     # Test suite (pytest)
├── data/samples/              # Toy demo files
├── diagnostic/                # Rule configurations
└── docs/                      # Documentation
```

## Memory Bank Priorities

**High Priority Context:**
1. Environment setup patterns (venv + PYTHONPATH)
2. Namespace detection rules (toy vs real ONIX)
3. Validation pipeline flow (XSD → Schematron → Rules)
4. Client deliverable requirements (Tufte + evidence tags)

**Medium Priority:**
1. CLI command patterns
2. Test execution workflows
3. Git commit conventions

**Low Priority:**
1. Specific file paths (can be discovered)
2. Implementation details (can be read)

---

*This document provides complete project context for optimizing Claude Desktop workflows. Use it to establish Memory Bank entries and MCP configurations that maintain project-specific best practices.*