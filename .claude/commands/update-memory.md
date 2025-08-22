---
name: update-memory
---
Intelligently update memory bank based on current session

1. Analyze current session to identify:
   - What code files were modified
   - What tests were run and their results
   - What decisions were made
   - What problems were encountered
   - What tasks were completed

2. Read existing memory-bank files:
   - Read memory-bank/active-context.md
   - Read memory-bank/progress.md  
   - Read memory-bank/decision-log.md
   - Read memory-bank/system-patterns.md

3. Categorize session changes:
   - ENVIRONMENT: Changes to setup, paths, dependencies
   - TESTS: New test count, failures, additions
   - PROGRESS: Tasks completed from the checklist
   - DECISIONS: Architectural choices with rationale
   - PATTERNS: New code patterns or validation rules discovered
   - BLOCKERS: New issues encountered

4. Update only what changed:
   - For active-context.md: Update test count, current task, blockers
   - For progress.md: Mark completed items, add new tasks discovered
   - For decision-log.md: Add only NEW decisions with date stamp
   - For system-patterns.md: Add only NEW patterns not already documented

5. Preserve existing content:
   - Never delete existing entries
   - Append new decisions with dates
   - Update counts and statuses
   - Mark completed tasks with [x]

6. Report what was updated:
   "Updated memory-bank:
    - active-context.md: Updated test count from 8 to 10
    - progress.md: Marked 'Tufte dashboard' complete
    - decision-log.md: Added decision about React vs vanilla JS
    - No changes needed to system-patterns.md"

IMPORTANT: 
- Read each file BEFORE updating
- Only update what actually changed this session
- Use git diff to see what code files changed
- Preserve all existing historical entries
