#!/bin/bash
# Core function testing script for MetaOps Validator
# Run this to verify all core functions are working

echo "==================================="
echo "MetaOps Validator Core Function Test"
echo "==================================="
echo ""

# Setup environment
source .venv/bin/activate
export PYTHONPATH=/home/ed/meta-ops-validator/src

echo "1. Testing XSD Validation..."
echo "----------------------------"
python -m metaops.cli.main validate-xsd \
    --onix data/samples/onix_samples/sample.xml \
    --xsd data/samples/onix_samples/onix.xsd
echo ""

echo "2. Testing Schematron Validation..."
echo "-----------------------------------"
python -m metaops.cli.main validate-schematron \
    --onix data/samples/onix_samples/sample.xml \
    --sch data/samples/onix_samples/rules.sch
echo ""

echo "3. Testing Rule DSL Engine..."
echo "-----------------------------"
python -m metaops.cli.main run-rules \
    --onix data/samples/onix_samples/sample.xml \
    --rules diagnostic/rules.sample.yml
echo ""

echo "4. Running Python Test Suite..."
echo "-------------------------------"
python -m pytest tests/ -v --tb=short
echo ""

echo "==================================="
echo "Test Complete"
echo "==================================="
echo ""
echo "To test the GUI:"
echo "1. Run: streamlit run streamlit_app.py"
echo "2. Open: http://localhost:8501"
echo "3. Upload files from data/samples/onix_samples/"