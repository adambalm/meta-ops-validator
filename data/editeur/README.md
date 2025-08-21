# Official EDItEUR ONIX 3.x Artifacts

**⚠️ CRITICAL: The current system uses TOY SCHEMAS for demo purposes only.**

To switch to production validation with real ONIX 3.x files, you must obtain and place the following official EDItEUR artifacts in this directory:

## Required Files

### 1. ONIX 3.x Schema (XSD)
Download from: https://www.editeur.org/15/Archived-Previous-Releases/

Place here:
- `onix-3.x-reference.xsd` (reference tag schema)
- `onix-3.x-short.xsd` (short tag schema)  
- Any additional schema files (typically a zip bundle)

### 2. EDItEUR Codelists (Latest Issue)
Download from: https://www.editeur.org/14/Code-Lists/

Place here:
- `codelists/` directory containing CSV or XML files for all lists
- Key lists needed: ProductForm, ProductFormDetail, PublishingDateRole, TerritoryCodeType, etc.

### 3. Sample Real ONIX Files (optional)
Place real anonymized ONIX 3.x samples in:
- `samples/real/` directory
- Both reference and short-tag variants recommended
- Use for regression testing against toy validation

## Namespace Variants

ONIX 3.x supports two tag formats:

**Reference tags:**
```xml
<ONIXMessage xmlns="http://ns.editeur.org/onix/3.0/reference">
  <Product>
    <DescriptiveDetail>
      <ProductForm>BC</ProductForm>
    </DescriptiveDetail>
  </Product>
</ONIXMessage>
```

**Short tags:**  
```xml
<ONIXmessage xmlns="http://ns.editeur.org/onix/3.0/short">
  <product>
    <descriptivedetail>  
      <b012>BC</b012>
    </descriptivedetail>
  </product>
</ONIXmessage>
```

## Integration Steps

Once files are placed here:

1. **Update configuration** to point validators at real schemas
2. **Implement codelists.py** to load official code mappings  
3. **Replace toy Schematron** with namespace-aware rules
4. **Update Rule DSL examples** to use proper ONIX XPaths with namespaces
5. **Run regression tests** to ensure toy→real migration works

## Validation Checklist

Before going to production:
- [ ] XSD validation passes on real ONIX files
- [ ] Schematron rules use proper namespaces  
- [ ] Rule DSL uses namespace-aware XPaths
- [ ] Codelists loaded and referenced correctly
- [ ] Both reference and short-tag variants supported
- [ ] Territory logic uses includes/excludes, not substring matching
- [ ] Date logic handles roles and dateformat properly
- [ ] Product form logic uses official codes + details

## Legal Note

EDItEUR artifacts are subject to their licensing terms. Ensure compliance with EDItEUR's usage policies for commercial applications.