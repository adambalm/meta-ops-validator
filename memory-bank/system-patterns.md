# MetaOps System Patterns

## Validation Pipeline Pattern
Always follow this flow:
1. Namespace detection (onix_utils.py)
2. XSD validation (validators/onix_xsd.py)
3. Schematron validation (validators/onix_schematron.py)
4. Rule DSL validation (rules/engine.py)
5. Report generation (reporters/)

## ONIX Namespace Pattern
ALWAYS for client materials:
<onix:Product xmlns:onix="http://ns.editeur.org/onix/3.0/reference">
  <onix:RecordReference>...</onix:RecordReference>
</onix:Product>

NEVER in client materials:
<Product>
  <RecordReference>...</RecordReference>
</Product>

## CLI Command Patterns
Validation commands (always with activated venv):
python -m metaops.cli.main validate-xsd --onix FILE --xsd SCHEMA
python -m metaops.cli.main validate-schematron --onix FILE --sch RULES
python -m metaops.cli.main run-rules --onix FILE --rules YAML

## Data Compliance Pattern
ALWAYS CHECK:
- Is data source public API or official sample?
- Are ISBNs real and verified?
- Is metric tagged [verified] or [inference]?
- Does ONIX example use proper namespace?

## Tufte Visual Pattern
- Tables over charts for precision
- Maximize data-ink ratio
- No 3D, gradients, or animations
- Small multiples for comparisons
- Evidence tags on all metrics

## Language Standards Pattern (ENFORCED)
NEVER use in code or documentation:
- "enterprise-ready" / "production-ready" 
- "enterprise-grade" / "production-grade"
- Similar exaggerated capability claims

ALWAYS use realistic language:
- "operational" instead of "production-ready"
- "functional" instead of "enterprise-ready"  
- "working" instead of "ready for production"
- "complete" instead of "production-grade"

## File Organization Pattern (NEW)
Logical directory structure for maintainability:
```
/specs/                     # All specifications
├── architecture/           # Technical architecture docs
├── business/              # Business requirements
├── technical/             # Technical and API specs
└── ui-ux/                # UI design and help content

/docs/                     # User and developer documentation  
├── user-guides/           # End-user documentation
├── governance/            # Project governance
└── [other doc categories]

/context/                  # Claude context files
├── CLAUDE_BUSINESS.md     # Business context
├── CLAUDE_TECHNICAL.md    # Technical context  
└── [other context files]
```

Use git mv for all file moves to preserve history.
Update all file references after reorganization.

## Test Quality Pattern (NEW)
Comprehensive validation requires all tests to pass:
- Fix ambiguous Playwright selectors (use specific elements vs text)
- Match test expectations to actual UI behavior
- Use `[data-testid="stApp"]` vs `main` for Streamlit apps
- Fix real bugs discovered during testing (don't ignore failures)
- UI tests validate actual usability, not just technical function

## Bug Fix Priority Pattern (NEW)
Always fix discovered bugs during refactoring:
1. **Functional bugs** - Missing keys, incorrect logic, API issues
2. **Code quality** - Deprecation warnings, async patterns  
3. **Test reliability** - Selector precision, timeout handling
4. **User experience** - UI navigation, tooltip accessibility

Better to delay feature work to fix quality issues.