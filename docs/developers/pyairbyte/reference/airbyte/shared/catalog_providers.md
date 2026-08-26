---
id: airbyte-shared-catalog_providers
title: airbyte.shared.catalog_providers
---

Catalog provider implementation.

A catalog provider wraps a configured catalog and configured streams. This class is responsible for
providing information about the catalog and streams. A catalog provider can also be updated with new
streams as they are discovered, providing a thin layer of abstraction over the configured catalog.

### `CatalogProvider` {#airbyte.shared.catalog_providers.CatalogProvider}

<ApiMember kind="class">

<ApiSignature>

```python
class CatalogProvider(configured_catalog: ConfiguredAirbyteCatalog)
```

</ApiSignature>

A catalog provider wraps a configured catalog and configured streams.

This class is responsible for providing information about the catalog and streams.

**Note:**

- The catalog provider is not responsible for managing the catalog or streams but it may
  be updated with new streams as they are discovered.

Initialize the catalog manager with a catalog object reference.

Since the catalog is passed by reference, the catalog manager may be updated with new
streams as they are discovered.

#### Attributes {#airbyte.shared.catalog_providers.CatalogProvider--attributes}

- **`configured_catalog`**&nbsp;(`ConfiguredAirbyteCatalog`) — Return the configured catalog.

- **`stream_names`**&nbsp;(`list[str]`) — Return the names of the streams in the catalog.

#### `from_read_result` {#airbyte.shared.catalog_providers.CatalogProvider.from_read_result}

<ApiMember kind="method">

<ApiSignature>

```python
def from_read_result(read_result: ReadResult)
```

</ApiSignature>

Create a catalog provider from a `ReadResult` object.

</ApiMember>

#### `validate_catalog` {#airbyte.shared.catalog_providers.CatalogProvider.validate_catalog}

<ApiMember kind="method">

<ApiSignature>

```python
def validate_catalog(catalog: ConfiguredAirbyteCatalog) -> None
```

</ApiSignature>

Validate the catalog to ensure it is valid.

This requires ensuring that `generationId` and `minGenerationId` are both set. If
not, both values will be set to `1`.

</ApiMember>

#### `get_configured_stream_info` {#airbyte.shared.catalog_providers.CatalogProvider.get_configured_stream_info}

<ApiMember kind="method">

<ApiSignature>

```python
def get_configured_stream_info(
    self,
    stream_name: str,
) -> ConfiguredAirbyteStream
```

</ApiSignature>

Return the column definitions for the given stream.

</ApiMember>

#### `get_cursor_key` {#airbyte.shared.catalog_providers.CatalogProvider.get_cursor_key}

<ApiMember kind="method">

<ApiSignature>

```python
def get_cursor_key(self, stream_name: str) -> str | None
```

</ApiSignature>

Return the cursor key for the given stream.

</ApiMember>

#### `get_primary_keys` {#airbyte.shared.catalog_providers.CatalogProvider.get_primary_keys}

<ApiMember kind="method">

<ApiSignature>

```python
def get_primary_keys(self, stream_name: str) -> list[str]
```

</ApiSignature>

Return the primary keys for the given stream.

</ApiMember>

#### `get_stream_json_schema` {#airbyte.shared.catalog_providers.CatalogProvider.get_stream_json_schema}

<ApiMember kind="method">

<ApiSignature>

```python
def get_stream_json_schema(self, stream_name: str) -> dict[str, typing.Any]
```

</ApiSignature>

Return the column definitions for the given stream.

</ApiMember>

#### `get_stream_properties` {#airbyte.shared.catalog_providers.CatalogProvider.get_stream_properties}

<ApiMember kind="method">

<ApiSignature>

```python
def get_stream_properties(self, stream_name: str) -> dict[str, dict]
```

</ApiSignature>

Return the names of the top-level properties for the given stream.

</ApiMember>

#### `resolve_write_method` {#airbyte.shared.catalog_providers.CatalogProvider.resolve_write_method}

<ApiMember kind="method">

<ApiSignature>

```python
def resolve_write_method(
    self,
    stream_name: str,
    write_strategy: WriteStrategy,
) -> airbyte.strategies.WriteMethod
```

</ApiSignature>

Return the write method for the given stream.

</ApiMember>

#### `with_write_strategy` {#airbyte.shared.catalog_providers.CatalogProvider.with_write_strategy}

<ApiMember kind="method">

<ApiSignature>

```python
def with_write_strategy(
    self,
    write_strategy: WriteStrategy,
) -> airbyte.shared.catalog_providers.CatalogProvider
```

</ApiSignature>

Return a new catalog provider with the specified write strategy applied.

The original catalog provider is not modified.

</ApiMember>

</ApiMember>