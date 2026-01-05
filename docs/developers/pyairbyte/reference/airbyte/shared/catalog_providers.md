---
sidebar_label: catalog_providers
title: airbyte.shared.catalog_providers
---

Catalog provider implementation.

A catalog provider wraps a configured catalog and configured streams. This class is responsible for
providing information about the catalog and streams. A catalog provider can also be updated with new
streams as they are discovered, providing a thin layer of abstraction over the configured catalog.

## annotations

## copy

## TYPE\_CHECKING

## Any

## final

## ConfiguredAirbyteCatalog

## exc

## LowerCaseNormalizer

## WriteMethod

## WriteStrategy

## CatalogProvider Objects

```python
class CatalogProvider()
```

A catalog provider wraps a configured catalog and configured streams.

This class is responsible for providing information about the catalog and streams.

**Notes**:

  - The catalog provider is not responsible for managing the catalog or streams but it may
  be updated with new streams as they are discovered.

#### \_\_init\_\_

```python
def __init__(configured_catalog: ConfiguredAirbyteCatalog) -> None
```

Initialize the catalog manager with a catalog object reference.

Since the catalog is passed by reference, the catalog manager may be updated with new
streams as they are discovered.

#### validate\_catalog

```python
@staticmethod
def validate_catalog(catalog: ConfiguredAirbyteCatalog) -> None
```

Validate the catalog to ensure it is valid.

This requires ensuring that `generationId` and `minGenerationId` are both set. If
not, both values will be set to `1`.

#### configured\_catalog

```python
@property
def configured_catalog() -> ConfiguredAirbyteCatalog
```

Return the configured catalog.

#### stream\_names

```python
@property
def stream_names() -> list[str]
```

Return the names of the streams in the catalog.

#### get\_configured\_stream\_info

```python
def get_configured_stream_info(stream_name: str) -> ConfiguredAirbyteStream
```

Return the column definitions for the given stream.

#### get\_stream\_json\_schema

```python
@final
def get_stream_json_schema(stream_name: str) -> dict[str, Any]
```

Return the column definitions for the given stream.

#### get\_stream\_properties

```python
def get_stream_properties(stream_name: str) -> dict[str, dict]
```

Return the names of the top-level properties for the given stream.

#### from\_read\_result

```python
@classmethod
def from_read_result(cls, read_result: ReadResult) -> CatalogProvider
```

Create a catalog provider from a `ReadResult` object.

#### get\_primary\_keys

```python
def get_primary_keys(stream_name: str) -> list[str]
```

Return the primary keys for the given stream.

#### get\_cursor\_key

```python
def get_cursor_key(stream_name: str) -> str | None
```

Return the cursor key for the given stream.

#### resolve\_write\_method

```python
def resolve_write_method(stream_name: str,
                         write_strategy: WriteStrategy) -> WriteMethod
```

Return the write method for the given stream.

#### with\_write\_strategy

```python
def with_write_strategy(write_strategy: WriteStrategy) -> CatalogProvider
```

Return a new catalog provider with the specified write strategy applied.

The original catalog provider is not modified.

