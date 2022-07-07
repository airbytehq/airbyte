Module airbyte_cdk.sources.utils.catalog_helpers
================================================

Classes
-------

`CatalogHelper()`
:   

    ### Static methods

    `coerce_catalog_as_full_refresh(catalog: airbyte_cdk.models.airbyte_protocol.AirbyteCatalog) ‑> airbyte_cdk.models.airbyte_protocol.AirbyteCatalog`
    :   Updates the sync mode on all streams in this catalog to be full refresh