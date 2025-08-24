# CLAUDE.md - MetaOps Validator

## ESSENTIAL SETUP (INVARIANT)

### Environment (EVERY SESSION)
source .venv/bin/activate
export PYTHONPATH=/home/ed/meta-ops-validator/src

### Validation Pipeline Order (INVARIANT)
1. XSD validation (validators/onix_xsd.py)
2. Schematron validation (validators/onix_schematron.py)  
3. Rule DSL validation (rules/engine.py)
4. Nielsen Completeness Scoring (validators/nielsen_scoring.py)
5. Retailer Compatibility Analysis (validators/retailer_profiles.py)

## CRITICAL RULES (INVARIANT)

### Namespace Compliance
Production requires namespace-aware XPath.
Client-facing ONIX MUST have namespaces.
See memory-bank/system-patterns.md for examples.

### Data Ethics
No scraping beyond public APIs.
Tag all metrics: [verified] or [inference].

### Visual Requirements  
Pure Tufte CSS. No chartjunk.

### Language Guidelines (INVARIANT)
NEVER use these terms in code or documentation:
- "production-ready" / "production ready" 
- "enterprise-ready" / "enterprise ready"
- "enterprise-grade" / "enterprise grade"
- Similar exaggerated claims

Use realistic language: "operational", "functional", "working", "complete".

### Web Services (CURRENT)
ONIX validation interfaces:
- Main Validator: http://100.111.114.84:8507 (streamlit_app.py) - Single file validation with tooltips
- Analytics Dashboard: http://100.111.114.84:8508 (dashboard.py) - Batch processing and analytics
- Business Demo: http://100.111.114.84:8090 (streamlit_business_demo.py) - Stakeholder presentations

Start services: streamlit run src/metaops/web/[app].py --server.port [PORT] --server.address 0.0.0.0

## PROJECT STATE (VARIABLE - CHECK MEMORY BANK)

### Current Status
See memory-bank/active-context.md for:
- Schema location (toy vs production)
- Test baseline count
- Current blockers

### Sprint Goals
See memory-bank/progress.md for:
- Current deadline
- Task checklist
- Completion status

### Technical Patterns
See memory-bank/system-patterns.md for:
- Code examples
- Namespace patterns
- Command templates

## UPDATE RULE

When making significant changes:
1. Update relevant memory-bank files
2. If adding new INVARIANT rules, update CLAUDE.md
3. On commit: "Update memory-bank with current state"

Example commit workflow:
- Complete feature
- "Update memory-bank/progress.md - mark X complete"
- "Update memory-bank/active-context.md with new test count"
- "Check if CLAUDE.md needs invariant updates"
- git commit

## AVAILABLE TOOLS

MCP Servers: memory-bank, github, refs, playwright
Web Services: Streamlit apps on ports 8507, 8508, 8090
UI Testing: Playwright MCP for automated usability evaluation
Test Files: test_onix_files/ (15 generated samples)
Detailed context: specs/ui-ux/tooltips-reference.md, specs/ui-ux/ui-specification.md
