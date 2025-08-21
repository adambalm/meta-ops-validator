<schema xmlns="http://purl.oclc.org/dsdl/schematron">
  <pattern id="basic">
    <rule context="Product/DescriptiveDetail">
      <assert test="ProductForm != 'AB'">Audio format 'AB' not allowed (demo)</assert>
    </rule>
    <rule context="Product/PublishingDetail">
      <assert test="string-length(normalize-space(PublishingDate)) &gt; 0">PublishingDate missing</assert>
    </rule>
  </pattern>
</schema>