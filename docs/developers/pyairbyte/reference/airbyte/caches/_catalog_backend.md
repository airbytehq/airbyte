---
sidebar_label: _catalog_backend
title: airbyte.caches._catalog_backend
---

Catalog backend implementation.

Catalog backend is responsible for storing and retrieving the stream catalog metadata to a durable
storage medium, such as an internal SQL table. It provides methods to register a source and its
streams in the cache, and to get catalog providers.

## annotations

## abc

## json

## TYPE\_CHECKING

## cast

## Column

## String

## Session

## declarative\_base

## AirbyteStream

## ConfiguredAirbyteCatalog

## ConfiguredAirbyteStream

## DestinationSyncMode

## SyncMode

## CatalogProvider

#### STREAMS\_TABLE\_NAME

#### SqlAlchemyModel

A base class to use for SQLAlchemy ORM models.

## CachedStream Objects

```python
class CachedStream(SqlAlchemyModel)
```

A SQLAlchemy ORM model to store stream catalog metadata.

#### \_\_tablename\_\_

#### stream\_name

#### source\_name

#### table\_name

#### catalog\_metadata

## CatalogBackendBase Objects

```python
class CatalogBackendBase(abc.ABC)
```

A class to manage the stream catalog of data synced to a cache.

This includes:
- What streams exist and to what tables they map
- The JSON schema for each stream

#### \_sql\_config

#### \_save\_catalog\_info

```python
@abc.abstractmethod
def _save_catalog_info(source_name: str,
                       incoming_source_catalog: ConfiguredAirbyteCatalog,
                       incoming_stream_names: set[str]) -> None
```

Serialize the incoming catalog information to storage.

**Raises**:

- `NotImplementedError` - If the catalog is static or the catalog manager is read only.

#### stream\_names

```python
@property
@abc.abstractmethod
def stream_names() -> list[str]
```

Return the names of all known streams in the catalog backend.

#### register\_source

```python
@abc.abstractmethod
def register_source(source_name: str,
                    incoming_source_catalog: ConfiguredAirbyteCatalog,
                    incoming_stream_names: set[str]) -> None
```

Register a source and its streams in the cache.

#### get\_full\_catalog\_provider

```python
@abc.abstractmethod
def get_full_catalog_provider() -> CatalogProvider
```

Return a catalog provider with the full catalog.

#### get\_source\_catalog\_provider

```python
@abc.abstractmethod
def get_source_catalog_provider(source_name: str) -> CatalogProvider
```

Return a catalog provider filtered for a single source.

## SqlCatalogBackend Objects

```python
class SqlCatalogBackend(CatalogBackendBase)
```

A class to manage the stream catalog of data synced to a cache.

This includes:
- What streams exist and to what tables they map
- The JSON schema for each stream.

#### \_\_init\_\_

```python
def __init__(sql_config: SqlConfig, table_prefix: str) -> None
```

#### \_ensure\_internal\_tables

```python
def _ensure_internal_tables() -> None
```

#### register\_source

```python
def register_source(source_name: str,
                    incoming_source_catalog: ConfiguredAirbyteCatalog,
                    incoming_stream_names: set[str]) -> None
```

Register a source and its streams in the cache.

#### \_save\_catalog\_info

```python
def _save_catalog_info(source_name: str,
                       incoming_source_catalog: ConfiguredAirbyteCatalog,
                       incoming_stream_names: set[str]) -> None
```

#### \_fetch\_streams\_info

```python
def _fetch_streams_info(
        *,
        source_name: str | None = None,
        table_prefix: str | None = None) -> list[ConfiguredAirbyteStream]
```

Fetch the streams information from the cache.

The `source_name` and `table_prefix` args are optional filters.

#### stream\_names

```python
@property
def stream_names() -> list[str]
```

#### get\_full\_catalog\_provider

```python
def get_full_catalog_provider() -> CatalogProvider
```

Return a catalog provider with the full catalog across all sources.

#### get\_source\_catalog\_provider

```python
def get_source_catalog_provider(source_name: str) -> CatalogProvider
```

