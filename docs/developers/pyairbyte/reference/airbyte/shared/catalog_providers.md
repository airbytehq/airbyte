---
id: airbyte-shared-catalog_providers
title: airbyte.shared.catalog_providers
---

Module airbyte.shared.catalog_providers
=======================================
Catalog provider implementation.

A catalog provider wraps a configured catalog and configured streams. This class is responsible for
providing information about the catalog and streams. A catalog provider can also be updated with new
streams as they are discovered, providing a thin layer of abstraction over the configured catalog.

Classes
-------

`CatalogProvider(configured_catalog: ConfiguredAirbyteCatalog)`
:   A catalog provider wraps a configured catalog and configured streams.
    
    This class is responsible for providing information about the catalog and streams.
    
    Note:
    - The catalog provider is not responsible for managing the catalog or streams but it may
      be updated with new streams as they are discovered.
    
    Initialize the catalog manager with a catalog object reference.
    
    Since the catalog is passed by reference, the catalog manager may be updated with new
    streams as they are discovered.

    ### Static methods

    `from_read_result(read_result: ReadResult)`
    :   Create a catalog provider from a `ReadResult` object.

    `validate_catalog(catalog: ConfiguredAirbyteCatalog) ‑> None`
    :   Validate the catalog to ensure it is valid.
        
        This requires ensuring that `generationId` and `minGenerationId` are both set. If
        not, both values will be set to `1`.

    ### Instance variables

    `configured_catalog: ConfiguredAirbyteCatalog`
    :   Return the configured catalog.

    `stream_names: list[str]`
    :   Return the names of the streams in the catalog.

    ### Methods

    `get_configured_stream_info(self, stream_name: str) ‑> ConfiguredAirbyteStream`
    :   Return the column definitions for the given stream.

    `get_cursor_key(self, stream_name: str) ‑> str | None`
    :   Return the cursor key for the given stream.

    `get_primary_keys(self, stream_name: str) ‑> list[str]`
    :   Return the primary keys for the given stream.

    `get_stream_json_schema(self, stream_name: str) ‑> dict[str, typing.Any]`
    :   Return the column definitions for the given stream.

    `get_stream_properties(self, stream_name: str) ‑> dict[str, dict]`
    :   Return the names of the top-level properties for the given stream.

    `resolve_write_method(self, stream_name: str, write_strategy: WriteStrategy) ‑> airbyte.strategies.WriteMethod`
    :   Return the write method for the given stream.

    `with_write_strategy(self, write_strategy: WriteStrategy) ‑> airbyte.shared.catalog_providers.CatalogProvider`
    :   Return a new catalog provider with the specified write strategy applied.
        
        The original catalog provider is not modified.