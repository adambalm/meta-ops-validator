# EDItEUR ONIX Codelists - Issue 70 (July 2025)

This directory contains the official EDItEUR ONIX codelists downloaded from https://www.editeur.org/14/code-lists/

## Files Downloaded

### Core Codelist Files
- `ONIX_BookProduct_Codelists_Issue_70.xml` - Complete codelists in XML format (1.4MB)
- `ONIX_BookProduct_Codelists_Issue_70.json` - Complete codelists in JSON format (1.3MB) 
- `ONIX_BookProduct_Codelists_Issue_70.csv` - Complete codelists in CSV format (576KB)

### Schema Files
- `ONIX_BookProduct_Codelists_Issue_70.zip` - Archive containing DTD, XSD, and RNG schema files (342KB)
- `ONIX_BookProduct_Codelist_Structure.xsd` - XSD schema for codelist XML structure (4.9KB)
- `ONIX_BookProduct_Codelists_Issue_70/` - Extracted directory containing:
  - `ONIX_BookProduct_CodeLists.dtd` - DTD schema (33KB)
  - `ONIX_BookProduct_CodeLists.xsd` - XSD schema (1.3MB)
  - `ONIX_BookProduct_CodeLists.rng` - RelaxNG schema (944KB)

### Test Files  
- `test_codelists.py` - Python script to verify XML parsing and structure

## Codelist Structure

The codelists contain **166 different code lists** covering all aspects of ONIX book metadata:

### Key Codelists Include:
- **List 1**: Notification or update type (9 codes)
- **List 2**: Product composition (7 codes)  
- **List 5**: Product identifier type (22 codes)
- **List 74**: Language codes (ISO 639-2/B, 487+ codes)
- **List 150**: Product form (90+ codes like BB=Hardback, BC=Paperback)
- **List 91**: Country codes (ISO 3166-1, 249+ codes)

### XML Structure
```xml
<ONIXCodeTable>
  <IssueNumber>70</IssueNumber>
  <CodeList>
    <CodeListNumber>1</CodeListNumber>
    <CodeListDescription>Notification or update type</CodeListDescription>
    <IssueNumber>0</IssueNumber>
    <Code>
      <CodeValue>01</CodeValue>
      <CodeDescription>Early notification</CodeDescription>
      <CodeNotes>Use for a complete record...</CodeNotes>
      <IssueNumber>0</IssueNumber>
      <ModifiedNumber/>
      <DeprecatedNumber/>
    </Code>
    <!-- More codes... -->
  </CodeList>
  <!-- More codelists... -->
</ONIXCodeTable>
```

### CSV Structure
The CSV format has 7 fields per row:
1. Code list number  
2. Code value
3. Label/description
4. Notes (optional)
5. Issue number when added
6. Last modified issue number  
7. Deprecated issue number

Example: `"150","BB","Hardback","Hardback or cased book","0","",""`

## Usage in ONIX Validation

These codelists are essential for validating ONIX files against the official standards:

1. **Code Validation**: Verify that coded values in ONIX elements match valid codes
2. **Reference Lookup**: Provide human-readable descriptions for codes
3. **Deprecation Checking**: Identify deprecated codes that should be avoided

## Testing

Run the validation test:
```bash
cd /home/ed/meta-ops-validator
source .venv/bin/activate
export PYTHONPATH=/home/ed/meta-ops-validator/src
python data/editeur/codelists/test_codelists.py
```

## License

These codelists are provided by EDItEUR under their standard license terms. See the XML file headers for full license details.

## Updates

This is Issue 70 from July 2025. EDItEUR typically releases new codelist issues quarterly. Check https://www.editeur.org/14/code-lists/ for updates.