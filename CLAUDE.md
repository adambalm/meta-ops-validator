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

MCP Servers: memory-bank, github, refs
Slash commands: /setup-env, /validate
Detailed context: CLAUDE_TECHNICAL.md, CLAUDE_BUSINESS.md
