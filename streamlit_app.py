from pathlib import Path
import pandas as pd
import streamlit as st
from metaops.validators.onix_xsd import validate_xsd
from metaops.validators.onix_schematron import validate_schematron
from metaops.rules.engine import evaluate as eval_rules
from metaops.onix_utils import detect_onix_namespace, is_using_toy_schemas

st.set_page_config(page_title="MetaOps Validator", layout="wide")
st.title("MetaOps Validator — Pre-Feed Checks & Ops KPIs (Demo)")

tab1, tab2, tab3 = st.tabs(["XSD Validation", "Schematron / Rule DSL", "Results Export"])

with tab1:
    st.subheader("ONIX XSD Validation")
    onix = st.file_uploader("Upload ONIX XML (toy or real)", type=["xml"], key="xsd_onix")
    xsd = st.file_uploader("Upload ONIX XSD (toy or real)", type=["xsd","xml"], key="xsd_schema")
    if st.button("Run XSD Validation", disabled=not(onix and xsd)):
        onix_path = Path("tmp_onix.xml"); onix_path.write_bytes(onix.read())
        xsd_path = Path("tmp_onix.xsd"); xsd_path.write_bytes(xsd.read())
        
        # Detect if using real ONIX with toy schema
        namespace_uri, is_real_onix = detect_onix_namespace(onix_path)
        is_toy_schema = is_using_toy_schemas(xsd_path)
        
        if is_real_onix and is_toy_schema:
            st.error("⚠️ Real ONIX file detected but using toy XSD schema!")
            st.warning("For production validation, replace with official EDItEUR ONIX 3.x schema from data/editeur/")
        elif is_real_onix:
            st.success(f"✅ Real ONIX file detected (namespace: {namespace_uri})")
        else:
            st.info("ℹ️ Using toy/demo ONIX format")
            
        rows = validate_xsd(onix_path, xsd_path)
        df = pd.DataFrame(rows)
        st.metric("Issues", len(df))
        if not df.empty: st.dataframe(df, use_container_width=True)
        st.session_state["xsd_rows"] = rows

with tab2:
    st.subheader("Schematron & Contract-Aware Rule DSL")
    onix2 = st.file_uploader("Upload ONIX XML", type=["xml"], key="sch_onix")
    sch = st.file_uploader("Upload Schematron (.sch)", type=["sch"], key="sch_schema")
    rules = st.file_uploader("Upload Rule DSL (YAML)", type=["yml","yaml"], key="dsl_rules")
    colA, colB = st.columns(2)
    with colA:
        if st.button("Run Schematron", disabled=not(onix2 and sch)):
            onix_path = Path("tmp_onix2.xml"); onix_path.write_bytes(onix2.read())
            sch_path = Path("tmp_rules.sch"); sch_path.write_bytes(sch.read())
            
            # Check for namespace compatibility
            namespace_uri, is_real_onix = detect_onix_namespace(onix_path)
            if is_real_onix:
                st.warning("⚠️ Real ONIX detected. Ensure Schematron rules use proper namespaces!")
                
            rows = validate_schematron(onix_path, sch_path)
            df = pd.DataFrame(rows)
            st.metric("Findings", len(df))
            if not df.empty: st.dataframe(df, use_container_width=True)
            st.session_state["sch_rows"] = rows
    with colB:
        if st.button("Run Rule DSL", disabled=not(onix2 and rules)):
            onix_path = Path("tmp_onix3.xml"); onix_path.write_bytes(onix2.read())
            rules_path = Path("tmp_rules.yaml"); rules_path.write_bytes(rules.read())
            
            # Check for namespace compatibility 
            namespace_uri, is_real_onix = detect_onix_namespace(onix_path)
            if is_real_onix:
                st.warning("⚠️ Real ONIX detected. Ensure Rule DSL XPaths use namespace prefixes (//onix:Product)!")
                
            rows = eval_rules(onix_path, rules_path)
            df = pd.DataFrame(rows)
            st.metric("Rule Findings", len(df))
            if not df.empty: st.dataframe(df, use_container_width=True)
            st.session_state["dsl_rows"] = rows

with tab3:
    st.subheader("Export Combined Results")
    combined = []
    for key in ("xsd_rows","sch_rows","dsl_rows"):
        if key in st.session_state and st.session_state[key]:
            for r in st.session_state[key]:
                r["_source"] = key
                combined.append(r)
    df = pd.DataFrame(combined)
    st.metric("Total Findings", len(df))
    if not df.empty:
        st.dataframe(df, use_container_width=True)
        st.download_button("Download CSV", data=df.to_csv(index=False).encode("utf-8"),
                           file_name="metaops_findings.csv", mime="text/csv")
        st.download_button("Download JSON", data=df.to_json(orient="records", indent=2).encode("utf-8"),
                           file_name="metaops_findings.json", mime="application/json")
    else:
        st.info("Run validations first, then export.")