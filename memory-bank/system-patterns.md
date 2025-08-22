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
