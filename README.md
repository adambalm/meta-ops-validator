# MetaOps Validator — PRD & Build Spec (v0.4)

**⚠️ IMPORTANT: Current implementation uses TOY SCHEMAS for demo purposes only.**  
**For production use with real ONIX 3.x files, see `data/editeur/README.md` for migration instructions.**

**Offer:** Pre-Feed Validator + Ops KPI Instrumentation (ONIX XSD + Schematron + contract-aware rule DSL).  
**Goal:** Financial security ≤ 6 months via paid diagnostic → 3-month trial-hire.  
**Guardrails:** No retailer scraping; API/docs-first; robots-respecting presence checks only.

## Demo vs Production

**Current Status (Demo):**
- ✅ CLI and GUI working with toy ONIX samples
- ✅ XSD, Schematron, and Rule DSL validation pipeline
- ✅ Namespace detection and compatibility warnings
- ❌ Uses simplified toy schemas (not real ONIX 3.x)
- ❌ No official EDItEUR codelist integration
- ❌ XPaths not namespace-aware for real ONIX files

**Production Readiness Checklist:**
- [ ] Replace toy XSD with official EDItEUR ONIX 3.x schema
- [ ] Load official EDItEUR codelists (ProductForm, Territory, etc.)
- [ ] Update all XPaths to be namespace-aware
- [ ] Replace toy Schematron with publisher/EDItEUR rules
- [ ] Test against real ONIX 3.x files (reference & short-tag)
- [ ] Implement proper Territory composite parsing
- [ ] Add date format validation with roles

**Migration Path:** See `data/editeur/README.md` for detailed instructions.

## CLI
- metaops validate-xsd — XSD validation
- metaops validate-schematron — Schematron validation
- metaops run-rules — YAML rule DSL over ONIX
- metaops score-presence — presence scoring (CSV/API cache only)
- metaops report — HTML summary from JSON runs

## GUI
Run `streamlit run streamlit_app.py` and upload sample files from `data/samples/onix_samples`.

## Quickstart
python -m venv .venv && source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
streamlit run streamlit_app.py