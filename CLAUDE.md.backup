# CLAUDE.md - MetaOps Validator Project Guide

This project has multiple Claude contexts depending on what you're building.

## Quick Start: What Are You Working On?

### 🔧 Technical Validation Core
**File:** `CLAUDE_TECHNICAL.md`
**Use when:**
- Building/modifying validation engines (XSD, Schematron, Rule DSL)
- Working with ONIX parsers and namespace detection
- Implementing KPI calculations
- Writing tests for validators

**Key commands:**
```bash
python -m metaops.cli.main validate-xsd --onix data/samples/onix_samples/sample.xml
python -m pytest tests/
```

### 💼 Business/Demo Layer
**File:** `CLAUDE_BUSINESS.md`
**Use when:**
- Creating client deliverables (reports, decks, proposals)
- Building demo dashboards
- Generating sales materials
- Preparing diagnostic artifacts

**Key commands:**
```bash
python presentation/reports/render_reports.py presentation/sample_data/report_inputs.yml
streamlit run streamlit_app.py
```

### 🔗 Integration Layer
**File:** `CLAUDE_INTEGRATION.md` (Future)
**Use when:**
- Connecting business dashboard to validator
- Setting up data pipelines
- Building API endpoints
- Orchestrating diagnostic workflows

## Project Overview

MetaOps Validator is a pre-feed ONIX validation system with operational KPI instrumentation, 
designed to win $4,950 diagnostics that convert to $7.5-10K/month contracts with enterprise publishers.

**Current Phase:** Building demo for S&S outreach (August 2025)
**Technical Status:** Core validator working with toy schemas, ready for EDItEUR migration
**Business Status:** Need compelling demo with real S&S public data

## Critical Principles Across All Contexts

1. **Data Ethics:** No unauthorized scraping. Public APIs and permitted data only.
2. **Evidence Hygiene:** Tag everything [verified] or [inference]
3. **Visual Identity:** Pure Tufte CSS across all client-facing materials
4. **Namespace Discipline:** All ONIX examples must use proper namespaces
5. **KPI Focus:** Error rate, TTR, incident prevention - not vanity metrics

## Which Context Do You Need?

Ask yourself:
- Am I writing Python validation code? → `CLAUDE_TECHNICAL.md`
- Am I creating something a client will see? → `CLAUDE_BUSINESS.md`  
- Am I connecting business to technical? → `CLAUDE_INTEGRATION.md`
- Am I unsure? → Start here and read the overview

## File Organization

```
src/metaops/          # Technical validation core (see CLAUDE_TECHNICAL.md)
presentation/         # Business/demo layer (see CLAUDE_BUSINESS.md) - TO BE CREATED
  ├── reports/        # Jinja2 templates for deliverables
  ├── demo-app/       # React dashboard
  └── sample_data/    # Demo data (public/reconstructed)
toolkit/              # Sales and marketing materials - TO BE CREATED
  ├── brief/          # 2-page Tufte brief
  ├── emails/         # Outreach sequences
  └── proposals/      # SOW templates
artifacts/            # Generated client deliverables - TO BE CREATED
diagnostic/           # Rules and diagnostic configurations
data/                 # Sample ONIX files and schemas
  ├── samples/        # Toy demo files
  └── editeur/        # Future: Official EDItEUR schemas
tests/                # Test suite
streamlit_app.py      # Current GUI interface
```

## Environment Setup

```bash
# For all contexts
python3 -m venv .venv && source .venv/bin/activate

# Technical work
pip install -r requirements.txt

# Business/demo work (when implemented)
pip install jinja2 pyyaml
# cd presentation/demo-app && npm install  # Future
```

## Current Sprint Goals (August 21-31, 2025)

1. ✅ Technical validator working with toy schemas
2. 🔄 Build Tufte-styled demo dashboard with S&S public data
3. 📝 Generate diagnostic deliverable templates
4. 📧 Create sales toolkit for outreach
5. 🎯 Send Tim the "I found your money" email by Aug 31

---

*Choose your context file based on your task. When in doubt, start here.*