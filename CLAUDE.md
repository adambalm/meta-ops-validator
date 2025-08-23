# CLAUDE.md - MetaOps Validator

## ESSENTIAL SETUP (INVARIANT)

### Environment (EVERY SESSION)
source .venv/bin/activate
export PYTHONPATH=/home/ed/meta-ops-validator/src

### Validation Pipeline Order (INVARIANT)
1. XSD validation (validators/onix_xsd.py)
2. Schematron validation (validators/onix_schematron.py)  
3. Rule DSL validation (rules/engine.py)

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

### Demo Deployment (CURRENT)
Business-ready demo services at:
- Business Demo: http://100.111.114.84:8090 (streamlit_business_demo.py)
- Dashboard: http://100.111.114.84:8082/demo.html
- Executive Report: http://100.111.114.84:8082/../reports/executive_summary.html

Web server: python web_server.py (manages multiple services)

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
Web Services: web_server.py (ports 8090, 8082)
Detailed context: CLAUDE_TECHNICAL.md, CLAUDE_BUSINESS.md
