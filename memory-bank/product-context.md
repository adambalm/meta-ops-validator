# MetaOps Validator Product Context

## Project Identity
- **Product:** Pre-Feed ONIX validation system
- **Target:** Enterprise publishers (Simon & Schuster initial)
- **Pricing:** $4,950 diagnostic → $7.5-10K/month contracts
- **Demo Deadline:** August 31, 2025

## Architecture Overview
- **Validation Pipeline:** XSD → Schematron → Rule DSL
- **Interfaces:** CLI (Typer) + GUI (Streamlit)
- **Current State:** Demo-ready with toy schemas
- **Migration Target:** EDItEUR production schemas

## Three-Context Architecture
1. **TECHNICAL:** Core validation, parsers, tests
2. **BUSINESS:** Client deliverables, demos, sales
3. **INTEGRATION:** (Future) Dashboard connections

## Critical Business Rules
- ALL client-facing ONIX must use proper namespaces
- Visual identity: Pure Tufte CSS (no chartjunk)
- Data compliance: [verified] vs [inference] tags
- Never scrape retailers beyond public APIs
