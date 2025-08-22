---
name: check-memory
---
Check what needs updating in memory bank

1. Run git status to see uncommitted changes
2. Check if test count changed: python -m pytest --co -q | wc -l
3. Read memory-bank/active-context.md
4. Compare current state to memory state
5. Report what's out of sync:
   - "Test count: Memory says 8, actual is 10"
   - "Uncommitted changes in: src/validators/onix_xsd.py"
   - "Progress not updated for completed tasks"
