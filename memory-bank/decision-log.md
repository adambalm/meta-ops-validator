# MetaOps Decision Log

## 2025-08-22: Memory Bank Implementation
**Context:** Need persistent memory across Claude sessions
**Decision:** Implement Memory Bank + MCP servers for context
**Alternatives:** Manual context files only
**Rationale:** Reduces context loss, improves workflow efficiency

## 2024-XX-XX: Three-Context Architecture
**Context:** Different tasks need different Claude instructions
**Decision:** Separate TECHNICAL, BUSINESS, INTEGRATION contexts
**Alternatives:** Single CLAUDE.md file
**Rationale:** Prevents context pollution, improves focus

## 2024-XX-XX: Toy Schema Strategy
**Context:** Need working demo before EDItEUR licensing
**Decision:** Use toy schemas with namespace detection warnings
**Alternatives:** Wait for production schemas
**Rationale:** Allows immediate development and testing

## 2024-XX-XX: Tufte CSS Visual Identity
**Context:** Need professional client-facing materials
**Decision:** Pure Tufte CSS with no chartjunk
**Alternatives:** Modern dashboards with animations
**Rationale:** Data-forward approach matches enterprise expectations

## Self-contained demo with embedded samples
- **Date:** 2025-08-23 11:48:37 PM
- **Author:** Unknown User
- **Context:** Remote demo access required zero-friction experience without file upload dependencies
- **Decision:** Created streamlit_business_demo.py with embedded sample files loaded from server filesystem, eliminating need for users to upload ONIX files during demonstrations
- **Alternatives Considered:** 
  - File upload interface (rejected - friction)
  - Remote file server (rejected - complexity)
  - Pre-loaded sample selection (rejected - limited scope)
- **Consequences:** 
  - Demo works immediately without setup
  - Business context integrated into interface
  - Professional presentation suitable for stakeholders
  - Requires server filesystem access to sample files

## Tailnet IP addressing for demo services
- **Date:** 2025-08-23 11:48:43 PM
- **Author:** Unknown User
- **Context:** Services needed to be accessible from remote Mac Pro at 100.91.110.24 on same tailnet
- **Decision:** Configured all web services to bind to 0.0.0.0 and reference tailnet IP 100.111.114.84 in URLs
- **Alternatives Considered:** 
  - Localhost URLs (rejected - not accessible)
  - Dynamic IP detection (rejected - unnecessary complexity)
  - Port forwarding (rejected - additional setup)
- **Consequences:** 
  - Services immediately accessible across tailnet
  - No additional network configuration required
  - Clean URLs for business demonstrations
  - Hard-coded IP requires update if server changes
