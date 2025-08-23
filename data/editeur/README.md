# Official EDItEUR ONIX 3.0 Schemas — ACTIVE

**✅ OPERATIONAL: This directory contains official EDItEUR ONIX 3.0 schemas currently in use.**

The MetaOps Validator system automatically uses these official schemas for enterprise ONIX validation:

## Active Schema Files ✅

### ONIX 3.0 XSD Schemas (In Use)
- `ONIX_BookProduct_3.0_reference.xsd` - Official reference tag schema
- `ONIX_BookProduct_3.0_short.xsd` - Official short tag schema  
- `ONIX_BookProduct_CodeLists.xsd` - EDItEUR codelists
- `ONIX_XHTML_Subset.xsd` - XHTML subset definitions

### Schematron Rules (In Use)
- `schematron/onix-production-rules.sch` - Business logic validation rules

## Automatic Schema Selection ✅

The validation system automatically:
1. **Detects ONIX namespace** in uploaded files
2. **Selects appropriate schema** (reference vs short-tag)  
3. **Validates with official EDItEUR rules**
4. **Provides real validation results**

## Namespace Variants Supported ✅

**Reference tags (detected automatically):**
```xml
<ONIXMessage xmlns="http://ns.editeur.org/onix/3.0/reference">
  <Product>
    <DescriptiveDetail>
      <ProductForm>BC</ProductForm>
    </DescriptiveDetail>
  </Product>
</ONIXMessage>
```

**Short tags (detected automatically):**  
```xml
<ONIXmessage xmlns="http://ns.editeur.org/onix/3.0/short">
  <product>
    <descriptivedetail>  
      <b012>BC</b012>
    </descriptivedetail>
  </product>
</ONIXmessage>
```

## Validation Capabilities ✅

The system provides enterprise-ready validation:
- ✅ XSD structural validation against official schemas
- ✅ Schematron business rules validation
- ✅ Nielsen completeness scoring with sales correlation
- ✅ Multi-retailer compatibility analysis
- ✅ Custom rule engine for publisher-specific requirements
- ✅ Automatic namespace detection and handling
- ✅ Real ONIX error reporting with line numbers and context

## Web Interface Access

- **Main Validator**: [http://100.111.114.84:8507](http://100.111.114.84:8507)
- **Analytics Dashboard**: [http://100.111.114.84:8508](http://100.111.114.84:8508)
- **Business Demo**: [http://100.111.114.84:8090](http://100.111.114.84:8090)

## Legal Compliance ✅

These official EDItEUR schemas are used in compliance with EDItEUR's licensing terms for ONIX validation services.