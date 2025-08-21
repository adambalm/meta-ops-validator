<?xml version="1.0" encoding="UTF-8"?>
<!--
  ONIX 3.x Production Schematron Rules (Namespace-Aware Template)
  
  This is a TEMPLATE/SKELETON for real ONIX validation rules.
  Replace with actual publisher or EDItEUR-provided Schematron.
  
  Key differences from toy version:
  1. Uses proper ONIX namespaces (reference/short variants)
  2. References official EDItEUR codelists  
  3. Handles ONIX composites correctly (Territory, PublishingDate, etc.)
-->
<schema xmlns="http://purl.oclc.org/dsdl/schematron" 
        xmlns:onix="http://ns.editeur.org/onix/3.0/reference">
        
  <title>ONIX 3.x Production Validation Rules</title>
  
  <!-- Namespace declarations for both reference and short-tag variants -->
  <ns uri="http://ns.editeur.org/onix/3.0/reference" prefix="onix"/>
  <ns uri="http://ns.editeur.org/onix/3.0/short" prefix="onix-short"/>
  
  <!-- Pattern: Core Product Structure -->
  <pattern id="core-structure">
    <title>Core ONIX Product Structure</title>
    
    <rule context="onix:Product">
      <assert test="onix:ProductIdentifier">
        Product must have at least one ProductIdentifier
      </assert>
      
      <assert test="onix:DescriptiveDetail">
        Product must have DescriptiveDetail section
      </assert>
      
      <assert test="onix:PublishingDetail">
        Product must have PublishingDetail section  
      </assert>
    </rule>
  </pattern>
  
  <!-- Pattern: Product Form Validation (using codelists) -->
  <pattern id="product-form">
    <title>Product Form and Format Validation</title>
    
    <rule context="onix:DescriptiveDetail">
      <assert test="onix:ProductForm">
        DescriptiveDetail must specify ProductForm
      </assert>
      
      <!-- Example: Audio format restriction (replace with real business rules) -->
      <assert test="not(onix:ProductForm = 'AB')" role="warning">
        Audio format may require additional contract review
      </assert>
    </rule>
    
    <!-- This is where real codelist validation would occur -->
    <rule context="onix:ProductForm">
      <!-- TODO: Add codelist validation using external lookup -->
      <report test="string-length(normalize-space(.)) = 0">
        ProductForm cannot be empty
      </report>
    </rule>
  </pattern>
  
  <!-- Pattern: Territory Validation (proper composite handling) -->  
  <pattern id="territory">
    <title>Sales Territory Validation</title>
    
    <rule context="onix:SalesRights/onix:Territory">
      <!-- Real ONIX uses CountriesIncluded/CountriesExcluded structure -->
      <assert test="onix:CountriesIncluded or onix:RegionsIncluded">
        Territory must specify included countries or regions
      </assert>
      
      <!-- Example business rule: Check for excluded markets -->
      <!-- TODO: Replace with actual contract-based territory logic -->
      <assert test="not(contains(onix:CountriesExcluded, 'CA'))" role="warning">
        Territory excludes Canada - verify contract terms
      </assert>
    </rule>
  </pattern>
  
  <!-- Pattern: Publishing Date Validation (with roles) -->
  <pattern id="publishing-dates">
    <title>Publishing Date Validation</title>
    
    <rule context="onix:PublishingDetail">
      <assert test="onix:PublishingDate[onix:PublishingDateRole = '01']">
        Product must have publication date (role 01)
      </assert>
    </rule>
    
    <rule context="onix:PublishingDate">
      <assert test="onix:PublishingDateRole">
        PublishingDate must specify a role
      </assert>
      
      <assert test="onix:Date">
        PublishingDate must have a Date value
      </assert>
      
      <!-- TODO: Add date format validation based on @dateformat -->
    </rule>
  </pattern>
  
  <!-- Pattern: Identifier Validation -->
  <pattern id="identifiers">
    <title>Product Identifier Validation</title>
    
    <rule context="onix:ProductIdentifier">
      <assert test="onix:ProductIDType">
        ProductIdentifier must specify type
      </assert>
      
      <assert test="onix:IDValue">
        ProductIdentifier must have a value
      </assert>
      
      <!-- Example: ISBN-13 format check -->
      <assert test="not(onix:ProductIDType = '15') or string-length(normalize-space(onix:IDValue)) = 13" 
              role="error">
        ISBN-13 must be exactly 13 digits
      </assert>
    </rule>
  </pattern>
  
</schema>