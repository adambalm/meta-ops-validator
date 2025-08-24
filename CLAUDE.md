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

### Process Hygiene (INVARIANT)
CRITICAL: Maintain strict process and resource hygiene.

**Database Integrity:**
- NEVER create duplicate records that violate unique constraints
- Always use proper error handling for IntegrityError exceptions
- Clear test databases completely between runs: `rm -f /tmp/metaops_demo.db`
- Verify unique constraints are properly set in models: `unique=True`

**Process Management:**
- NEVER start processes without tracking them
- Before starting new services, check existing processes: `ps aux | grep -E "(streamlit|uvicorn)"`
- Use KillBash tool to properly terminate background processes
- NEVER abandon background processes - clean up after every session
- Use single ports per service type:
  - API: 8002 (uvicorn)  
  - Demo UI: 8003 (streamlit)
  - One service per port, kill before restarting

**Resource Cleanup:**
- Always clean up temporary files and databases
- Kill background processes at session end
- Remove duplicate ISBNs, authors, or other unique entities
- Clear caches and temporary storage between tests

**Before Starting Any Service:**
1. Check if port is in use: `lsof -ti:PORT` or `ps aux | grep PORT`
2. Kill existing process if needed: `pkill -f "service_name"`
3. Start new process with explicit environment variables
4. Track the process ID or use KillBash tool for cleanup

### Validation Requirements (INVARIANT)
NEVER claim completion without Playwright MCP validation.

**MANDATORY before claiming "working", "operational", "demo-ready", etc.:**
1. Use Task tool with publishing-ux-designer agent to test UI workflows
2. Use Playwright MCP to verify actual user experience
3. Test all major user paths (create book, generate ONIX, view dashboard)
4. Validate that data shows in UI, not just API endpoints

**Auto-enforcement pattern:**
- If claiming feature works → MUST show Playwright test results
- If claiming system ready → MUST show complete UI validation  
- If committing as "complete" → MUST include Playwright evidence
- NO EXCEPTIONS - API tests alone are insufficient

**Violation response:**
"I cannot claim this works without Playwright MCP validation. Let me test the actual user experience first."

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
