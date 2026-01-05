---
sidebar_label: base
title: airbyte.sources.base
---

Base class implementation for sources.

## annotations

## sys

## threading

## time

## warnings

## islice

## TYPE\_CHECKING

## Any

## Literal

## yaml

## print

## Console

## Markdown

## escape

## Table

## override

## AirbyteCatalog

## AirbyteMessage

## ConfiguredAirbyteCatalog

## ConfiguredAirbyteStream

## DestinationSyncMode

## SyncMode

## Type

## exc

## ConnectorBase

## AirbyteMessageIterator

## as\_temp\_files

## get\_default\_cache

## LazyDataset

## ProgressStyle

## ProgressTracker

## StreamRecord

## StreamRecordHandler

## ReadResult

## CatalogProvider

## WriteStrategy

## AB\_EXTRACTED\_AT\_COLUMN

## AB\_META\_COLUMN

## AB\_RAW\_ID\_COLUMN

## Source Objects

```python
class Source(ConnectorBase)
```

A class representing a source that can be called.

#### connector\_type

#### \_\_init\_\_

```python
def __init__(
        executor: Executor,
        name: str,
        config: dict[str, Any] | None = None,
        *,
        config_change_callback: ConfigChangeCallback | None = None,
        streams: str | list[str] | None = None,
        validate: bool = False,
        cursor_key_overrides: dict[str, str] | None = None,
        primary_key_overrides: dict[str, str | list[str]] | None = None
) -> None
```

Initialize the source.

If config is provided, it will be validated against the spec if validate is True.

#### set\_streams

```python
def set_streams(streams: list[str]) -> None
```

Deprecated. See select_streams().

#### set\_cursor\_key

```python
def set_cursor_key(stream_name: str, cursor_key: str) -> None
```

Set the cursor for a single stream.

**Notes**:

  - This does not unset previously set cursors.
  - The cursor key must be a single field name.
  - Not all streams support custom cursors. If a stream does not support custom cursors,
  the override may be ignored.
  - Stream names are case insensitive, while field names are case sensitive.
  - Stream names are not validated by PyAirbyte. If the stream name
  does not exist in the catalog, the override may be ignored.

#### set\_cursor\_keys

```python
def set_cursor_keys(**kwargs: str) -> None
```

Override the cursor key for one or more streams.

Usage:
source.set_cursor_keys(
stream1=&quot;cursor1&quot;,
stream2=&quot;cursor2&quot;,
)

**Notes**:

  - This does not unset previously set cursors.
  - The cursor key must be a single field name.
  - Not all streams support custom cursors. If a stream does not support custom cursors,
  the override may be ignored.
  - Stream names are case insensitive, while field names are case sensitive.
  - Stream names are not validated by PyAirbyte. If the stream name
  does not exist in the catalog, the override may be ignored.

#### set\_primary\_key

```python
def set_primary_key(stream_name: str, primary_key: str | list[str]) -> None
```

Set the primary key for a single stream.

**Notes**:

  - This does not unset previously set primary keys.
  - The primary key must be a single field name or a list of field names.
  - Not all streams support overriding primary keys. If a stream does not support overriding
  primary keys, the override may be ignored.
  - Stream names are case insensitive, while field names are case sensitive.
  - Stream names are not validated by PyAirbyte. If the stream name
  does not exist in the catalog, the override may be ignored.

#### set\_primary\_keys

```python
def set_primary_keys(**kwargs: str | list[str]) -> None
```

Override the primary keys for one or more streams.

This does not unset previously set primary keys.

Usage:
source.set_primary_keys(
stream1=&quot;pk1&quot;,
stream2=[&quot;pk1&quot;, &quot;pk2&quot;],
)

**Notes**:

  - This does not unset previously set primary keys.
  - The primary key must be a single field name or a list of field names.
  - Not all streams support overriding primary keys. If a stream does not support overriding
  primary keys, the override may be ignored.
  - Stream names are case insensitive, while field names are case sensitive.
  - Stream names are not validated by PyAirbyte. If the stream name
  does not exist in the catalog, the override may be ignored.

#### \_log\_warning\_preselected\_stream

```python
def _log_warning_preselected_stream(streams: str | list[str]) -> None
```

Logs a warning message indicating stream selection which are not selected yet.

#### select\_all\_streams

```python
def select_all_streams() -> None
```

Select all streams.

This is a more streamlined equivalent to:
&gt; source.select_streams(source.get_available_streams()).

#### select\_streams

```python
def select_streams(streams: str | list[str]) -> None
```

Select the stream names that should be read from the connector.

**Arguments**:

- `streams` - A list of stream names to select. If set to &quot;*&quot;, all streams will be selected.
  
  Currently, if this is not set, all streams will be read.

#### get\_selected\_streams

```python
def get_selected_streams() -> list[str]
```

Get the selected streams.

If no streams are selected, return an empty list.

#### set\_config

```python
def set_config(config: dict[str, Any], *, validate: bool = True) -> None
```

Set the config for the connector.

If validate is True, raise an exception if the config fails validation.

If validate is False, validation will be deferred until check() or validate_config()
is called.

#### \_discover

```python
def _discover() -> AirbyteCatalog
```

Call discover on the connector.

This involves the following steps:
- Write the config to a temporary file
- execute the connector with discover --config &lt;config_file&gt;
- Listen to the messages and return the first AirbyteCatalog that comes along.
- Make sure the subprocess is killed when the function returns.

#### get\_available\_streams

```python
def get_available_streams() -> list[str]
```

Get the available streams from the spec.

#### \_get\_incremental\_stream\_names

```python
def _get_incremental_stream_names() -> list[str]
```

Get the name of streams that support incremental sync.

#### \_get\_spec

```python
@override
def _get_spec(*, force_refresh: bool = False) -> ConnectorSpecification
```

Call spec on the connector.

This involves the following steps:
* execute the connector with spec
* Listen to the messages and return the first AirbyteCatalog that comes along.
* Make sure the subprocess is killed when the function returns.

#### config\_spec

```python
@property
def config_spec() -> dict[str, Any]
```

Generate a configuration spec for this connector, as a JSON Schema definition.

This function generates a JSON Schema dictionary with configuration specs for the
current connector, as a dictionary.

**Returns**:

- `dict` - The JSON Schema configuration spec as a dictionary.

#### \_yaml\_spec

```python
@property
def _yaml_spec() -> str
```

Get the spec as a yaml string.

For now, the primary use case is for writing and debugging a valid config for a source.

This is private for now because we probably want better polish before exposing this
as a stable interface. This will also get easier when we have docs links with this info
for each connector.

#### docs\_url

```python
@property
def docs_url() -> str
```

Get the URL to the connector&#x27;s documentation.

#### discovered\_catalog

```python
@property
def discovered_catalog() -> AirbyteCatalog
```

Get the raw catalog for the given streams.

If the catalog is not yet known, we call discover to get it.

#### configured\_catalog

```python
@property
def configured_catalog() -> ConfiguredAirbyteCatalog
```

Get the configured catalog for the given streams.

If the raw catalog is not yet known, we call discover to get it.

If no specific streams are selected, we return a catalog that syncs all available streams.

TODO: We should consider disabling by default the streams that the connector would
disable by default. (For instance, streams that require a premium license are sometimes
disabled by default within the connector.)

#### get\_configured\_catalog

```python
def get_configured_catalog(
        streams: Literal["*"] | list[str] | None = None,
        *,
        force_full_refresh: bool = False) -> ConfiguredAirbyteCatalog
```

Get a configured catalog for the given streams.

If no streams are provided, the selected streams will be used. If no streams are selected,
all available streams will be used.

If &#x27;*&#x27; is provided, all available streams will be used.

If force_full_refresh is True, streams will be configured with full_refresh sync mode
when supported by the stream. Otherwise, incremental sync mode is used when supported.

#### get\_stream\_json\_schema

```python
def get_stream_json_schema(stream_name: str) -> dict[str, Any]
```

Return the JSON Schema spec for the specified stream name.

#### get\_records

```python
def get_records(stream: str,
                *,
                limit: int | None = None,
                stop_event: threading.Event | None = None,
                normalize_field_names: bool = False,
                prune_undeclared_fields: bool = True) -> LazyDataset
```

Read a stream from the connector.

**Arguments**:

- `stream` - The name of the stream to read.
- `limit` - The maximum number of records to read. If None, all records will be read.
- `stop_event` - If set, the event can be triggered by the caller to stop reading records
  and terminate the process.
- `normalize_field_names` - When `True`, field names will be normalized to lower case, with
  special characters removed. This matches the behavior of PyAirbyte caches and most
  Airbyte destinations.
- `prune_undeclared_fields` - When `True`, undeclared fields will be pruned from the records,
  which generally matches the behavior of PyAirbyte caches and most Airbyte
  destinations, specifically when you expect the catalog may be stale. You can disable
  this to keep all fields in the records.
  
  This involves the following steps:
  * Call discover to get the catalog
  * Generate a configured catalog that syncs the given stream in full_refresh mode
  * Write the configured catalog and the config to a temporary file
  * execute the connector with read --config &lt;config_file&gt; --catalog &lt;catalog_file&gt;
  * Listen to the messages and return the first AirbyteRecordMessages that come along.
  * Make sure the subprocess is killed when the function returns.

#### get\_documents

```python
def get_documents(stream: str,
                  title_property: str | None = None,
                  content_properties: list[str] | None = None,
                  metadata_properties: list[str] | None = None,
                  *,
                  render_metadata: bool = False) -> Iterable[Document]
```

Read a stream from the connector and return the records as documents.

If metadata_properties is not set, all properties that are not content will be added to
the metadata.

If render_metadata is True, metadata will be rendered in the document, as well as the
the main content.

#### get\_samples

```python
def get_samples(
    streams: list[str] | Literal["*"] | None = None,
    *,
    limit: int = 5,
    on_error: Literal["raise", "ignore", "log"] = "raise"
) -> dict[str, InMemoryDataset | None]
```

Get a sample of records from the given streams.

#### print\_samples

```python
def print_samples(streams: list[str] | Literal["*"] | None = None,
                  *,
                  limit: int = 5,
                  on_error: Literal["raise", "ignore", "log"] = "log") -> None
```

Print a sample of records from the given streams.

#### \_get\_airbyte\_message\_iterator

```python
def _get_airbyte_message_iterator(
        *,
        streams: Literal["*"] | list[str] | None = None,
        state_provider: StateProviderBase | None = None,
        progress_tracker: ProgressTracker,
        force_full_refresh: bool = False) -> AirbyteMessageIterator
```

Get an AirbyteMessageIterator for this source.

#### \_read\_with\_catalog

```python
def _read_with_catalog(
    catalog: ConfiguredAirbyteCatalog,
    progress_tracker: ProgressTracker,
    *,
    state: StateProviderBase | None = None,
    stop_event: threading.Event | None = None
) -> Generator[AirbyteMessage, None, None]
```

Call read on the connector.

This involves the following steps:
* Write the config to a temporary file
* execute the connector with read --config &lt;config_file&gt; --catalog &lt;catalog_file&gt;
* Listen to the messages and return the AirbyteRecordMessages that come along.
* Send out telemetry on the performed sync (with information about which source was used and
  the type of the cache)

#### \_peek\_airbyte\_message

```python
def _peek_airbyte_message(message: AirbyteMessage,
                          *,
                          raise_on_error: bool = True) -> None
```

Process an Airbyte message.

This method handles reading Airbyte messages and taking action, if needed, based on the
message type. For instance, log messages are logged, records are tallied, and errors are
raised as exceptions if `raise_on_error` is True.

**Raises**:

- `AirbyteConnectorFailedError` - If a TRACE message of type ERROR is emitted.

#### \_log\_incremental\_streams

```python
def _log_incremental_streams(*,
                             incremental_streams: set[str] | None = None
                             ) -> None
```

Log the streams which are using incremental sync mode.

#### read

```python
def read(cache: CacheBase | None = None,
         *,
         streams: str | list[str] | None = None,
         write_strategy: str | WriteStrategy = WriteStrategy.AUTO,
         force_full_refresh: bool = False,
         skip_validation: bool = False) -> ReadResult
```

Read from the connector and write to the cache.

**Arguments**:

- `cache` - The cache to write to. If not set, a default cache will be used.
- `streams` - Optional if already set. A list of stream names to select for reading. If set
  to &quot;*&quot;, all streams will be selected.
- `write_strategy` - The strategy to use when writing to the cache. If a string, it must be
  one of &quot;append&quot;, &quot;merge&quot;, &quot;replace&quot;, or &quot;auto&quot;. If a WriteStrategy, it must be one
  of WriteStrategy.APPEND, WriteStrategy.MERGE, WriteStrategy.REPLACE, or
  WriteStrategy.AUTO.
- `force_full_refresh` - If True, the source will operate in full refresh mode. Otherwise,
  streams will be read in incremental mode if supported by the connector. This option
  must be True when using the &quot;replace&quot; strategy.
- `skip_validation` - If True, PyAirbyte will not pre-validate the input configuration before
  running the connector. This can be helpful in debugging, when you want to send
  configurations to the connector that otherwise might be rejected by JSON Schema
  validation rules.

#### \_read\_to\_cache

```python
def _read_to_cache(cache: CacheBase,
                   *,
                   catalog_provider: CatalogProvider,
                   stream_names: list[str],
                   state_provider: StateProviderBase | None,
                   state_writer: StateWriterBase | None,
                   write_strategy: str | WriteStrategy = WriteStrategy.AUTO,
                   force_full_refresh: bool = False,
                   skip_validation: bool = False,
                   progress_tracker: ProgressTracker) -> ReadResult
```

Internal read method.

#### \_\_all\_\_

