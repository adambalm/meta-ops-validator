---
name: validate
---
Run full validation on: $ARGUMENTS

1. Setup environment:
   source .venv/bin/activate
   export PYTHONPATH=/home/ed/meta-ops-validator/src

2. Run validation pipeline:
   - XSD validation
   - Schematron validation  
   - Rule DSL validation

3. Check for namespace issues

4. Generate report

5. Update memory-bank/active-context.md with results
