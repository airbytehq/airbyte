---
id: airbyte-sources-base
title: airbyte.sources.base
---

Base class implementation for sources.

### `Source` {#airbyte.sources.base.Source}

<ApiMember kind="class">

<ApiSignature>

```python
class Source(
    executor: Executor,
    name: str,
    config: dict[str, Any] | None = None,
    *,
    config_change_callback: ConfigChangeCallback | None = None,
    streams: str | list[str] | None = None,
    validate: bool = False,
    cursor_key_overrides: dict[str, str] | None = None,
    primary_key_overrides: dict[str, str | list[str]] | None = None,
)
```

</ApiSignature>

A class representing a source that can be called.

Initialize the source.

If config is provided, it will be validated against the spec if validate is True.

**Bases:** `airbyte._connector_base.ConnectorBase`, `abc.ABC`

#### Attributes {#airbyte.sources.base.Source--attributes}

- **`connector_type`**&nbsp;(`Literal['destination', 'source']`)

- **`config_spec`**&nbsp;(`dict[str, Any]`)

  Generate a configuration spec for this connector, as a JSON Schema definition.

  This function generates a JSON Schema dictionary with configuration specs for the
  current connector, as a dictionary.

  **Returns:**

  - **`dict`**: The JSON Schema configuration spec as a dictionary.

- **`configured_catalog`**&nbsp;(`ConfiguredAirbyteCatalog`)

  Get the configured catalog for the given streams.

  If the raw catalog is not yet known, we call discover to get it.

  If no specific streams are selected, we return a catalog that syncs all available streams.

  TODO: We should consider disabling by default the streams that the connector would
  disable by default. (For instance, streams that require a premium license are sometimes
  disabled by default within the connector.)

- **`discovered_catalog`**&nbsp;(`AirbyteCatalog`)

  Get the raw catalog for the given streams.

  If the catalog is not yet known, we call discover to get it.

- **`docs_url`**&nbsp;(`str`)

  Get the URL to the connector's documentation.

#### `get_available_streams` {#airbyte.sources.base.Source.get_available_streams}

<ApiMember kind="method">

<ApiSignature>

```python
def get_available_streams(self) -> list[str]
```

</ApiSignature>

Get the available streams from the spec.

</ApiMember>

#### `get_configured_catalog` {#airbyte.sources.base.Source.get_configured_catalog}

<ApiMember kind="method">

<ApiSignature>

```python
def get_configured_catalog(
    self,
    streams: "Literal['*'] | list[str] | None" = None,
    *,
    force_full_refresh: bool = False,
) -> airbyte_protocol.models.airbyte_protocol.ConfiguredAirbyteCatalog
```

</ApiSignature>

Get a configured catalog for the given streams.

If no streams are provided, the selected streams will be used. If no streams are selected,
all available streams will be used.

If '*' is provided, all available streams will be used.

If force_full_refresh is True, streams will be configured with full_refresh sync mode
when supported by the stream. Otherwise, incremental sync mode is used when supported.

</ApiMember>

#### `get_documents` {#airbyte.sources.base.Source.get_documents}

<ApiMember kind="method">

<ApiSignature>

```python
def get_documents(
    self,
    stream: str,
    title_property: str | None = None,
    content_properties: list[str] | None = None,
    metadata_properties: list[str] | None = None,
    *,
    render_metadata: bool = False,
) -> Iterable[Document]
```

</ApiSignature>

Read a stream from the connector and return the records as documents.

If metadata_properties is not set, all properties that are not content will be added to
the metadata.

If render_metadata is True, metadata will be rendered in the document, as well as the
the main content.

</ApiMember>

#### `get_records` {#airbyte.sources.base.Source.get_records}

<ApiMember kind="method">

<ApiSignature>

```python
def get_records(
    self,
    stream: str,
    *,
    limit: int | None = None,
    stop_event: threading.Event | None = None,
    normalize_field_names: bool = False,
    prune_undeclared_fields: bool = True,
) -> airbyte.datasets._lazy.LazyDataset
```

</ApiSignature>

Read a stream from the connector.

**Args:**

- **`stream`**: The name of the stream to read.
- **`limit`**: The maximum number of records to read. If None, all records will be read.
- **`stop_event`**: If set, the event can be triggered by the caller to stop reading records and terminate the process.
- **`normalize_field_names`**: When `True`, field names will be normalized to lower case, with special characters removed. This matches the behavior of PyAirbyte caches and most Airbyte destinations.
- **`prune_undeclared_fields`**: When `True`, undeclared fields will be pruned from the records, which generally matches the behavior of PyAirbyte caches and most Airbyte destinations, specifically when you expect the catalog may be stale. You can disable this to keep all fields in the records.

This involves the following steps:
* Call discover to get the catalog
* Generate a configured catalog that syncs the given stream in full_refresh mode
* Write the configured catalog and the config to a temporary file
* execute the connector with read --config &lt;config_file&gt; --catalog &lt;catalog_file&gt;
* Listen to the messages and return the first AirbyteRecordMessages that come along.
* Make sure the subprocess is killed when the function returns.

</ApiMember>

#### `get_samples` {#airbyte.sources.base.Source.get_samples}

<ApiMember kind="method">

<ApiSignature>

```python
def get_samples(
    self,
    streams: "list[str] | Literal['*'] | None" = None,
    *,
    limit: int = 5,
    on_error: "Literal['raise', 'ignore', 'log']" = 'raise',
) -> dict[str, InMemoryDataset | None]
```

</ApiSignature>

Get a sample of records from the given streams.

</ApiMember>

#### `get_selected_streams` {#airbyte.sources.base.Source.get_selected_streams}

<ApiMember kind="method">

<ApiSignature>

```python
def get_selected_streams(self) -> list[str]
```

</ApiSignature>

Get the selected streams.

If no streams are selected, return an empty list.

</ApiMember>

#### `get_stream_json_schema` {#airbyte.sources.base.Source.get_stream_json_schema}

<ApiMember kind="method">

<ApiSignature>

```python
def get_stream_json_schema(self, stream_name: str) -> dict[str, typing.Any]
```

</ApiSignature>

Return the JSON Schema spec for the specified stream name.

</ApiMember>

#### `print_samples` {#airbyte.sources.base.Source.print_samples}

<ApiMember kind="method">

<ApiSignature>

```python
def print_samples(
    self,
    streams: "list[str] | Literal['*'] | None" = None,
    *,
    limit: int = 5,
    on_error: "Literal['raise', 'ignore', 'log']" = 'log',
) -> None
```

</ApiSignature>

Print a sample of records from the given streams.

</ApiMember>

#### `read` {#airbyte.sources.base.Source.read}

<ApiMember kind="method">

<ApiSignature>

```python
def read(
    self,
    cache: CacheBase | None = None,
    *,
    streams: str | list[str] | None = None,
    write_strategy: str | WriteStrategy = WriteStrategy.AUTO,
    force_full_refresh: bool = False,
    skip_validation: bool = False,
) -> ReadResult
```

</ApiSignature>

Read from the connector and write to the cache.

**Args:**

- **`cache`**: The cache to write to. If not set, a default cache will be used.
- **`streams`**: Optional if already set. A list of stream names to select for reading. If set to "*", all streams will be selected.
- **`write_strategy`**: The strategy to use when writing to the cache. If a string, it must be one of "append", "merge", "replace", or "auto". If a WriteStrategy, it must be one of WriteStrategy.APPEND, WriteStrategy.MERGE, WriteStrategy.REPLACE, or WriteStrategy.AUTO.
- **`force_full_refresh`**: If True, the source will operate in full refresh mode. Otherwise, streams will be read in incremental mode if supported by the connector. This option must be True when using the "replace" strategy.
- **`skip_validation`**: If True, PyAirbyte will not pre-validate the input configuration before running the connector. This can be helpful in debugging, when you want to send configurations to the connector that otherwise might be rejected by JSON Schema validation rules.

</ApiMember>

#### `select_all_streams` {#airbyte.sources.base.Source.select_all_streams}

<ApiMember kind="method">

<ApiSignature>

```python
def select_all_streams(self) -> None
```

</ApiSignature>

Select all streams.

This is a more streamlined equivalent to:
> source.select_streams(source.get_available_streams()).

</ApiMember>

#### `select_streams` {#airbyte.sources.base.Source.select_streams}

<ApiMember kind="method">

<ApiSignature>

```python
def select_streams(self, streams: str | list[str]) -> None
```

</ApiSignature>

Select the stream names that should be read from the connector.

**Args:**

- **`streams`**: A list of stream names to select. If set to "*", all streams will be selected.

Currently, if this is not set, all streams will be read.

</ApiMember>

#### `set_config` {#airbyte.sources.base.Source.set_config}

<ApiMember kind="method">

<ApiSignature>

```python
def set_config(self, config: dict[str, Any], *, validate: bool = True) -> None
```

</ApiSignature>

Set the config for the connector.

If validate is True, raise an exception if the config fails validation.

If validate is False, validation will be deferred until check() or validate_config()
is called.

</ApiMember>

#### `set_cursor_key` {#airbyte.sources.base.Source.set_cursor_key}

<ApiMember kind="method">

<ApiSignature>

```python
def set_cursor_key(self, stream_name: str, cursor_key: str) -> None
```

</ApiSignature>

Set the cursor for a single stream.

**Note:**

- This does not unset previously set cursors.
- The cursor key must be a single field name.
- Not all streams support custom cursors. If a stream does not support custom cursors,
  the override may be ignored.
- Stream names are case insensitive, while field names are case sensitive.
- Stream names are not validated by PyAirbyte. If the stream name
  does not exist in the catalog, the override may be ignored.

</ApiMember>

#### `set_cursor_keys` {#airbyte.sources.base.Source.set_cursor_keys}

<ApiMember kind="method">

<ApiSignature>

```python
def set_cursor_keys(self, **kwargs: str) -> None
```

</ApiSignature>

Override the cursor key for one or more streams.

Usage:
    ```python
    source.set_cursor_keys(
        stream1="cursor1",
        stream2="cursor2",
    )
    ```

**Note:**

- This does not unset previously set cursors.
- The cursor key must be a single field name.
- Not all streams support custom cursors. If a stream does not support custom cursors,
  the override may be ignored.
- Stream names are case insensitive, while field names are case sensitive.
- Stream names are not validated by PyAirbyte. If the stream name
  does not exist in the catalog, the override may be ignored.

</ApiMember>

#### `set_primary_key` {#airbyte.sources.base.Source.set_primary_key}

<ApiMember kind="method">

<ApiSignature>

```python
def set_primary_key(
    self,
    stream_name: str,
    primary_key: str | list[str],
) -> None
```

</ApiSignature>

Set the primary key for a single stream.

**Note:**

- This does not unset previously set primary keys.
- The primary key must be a single field name or a list of field names.
- Not all streams support overriding primary keys. If a stream does not support overriding
  primary keys, the override may be ignored.
- Stream names are case insensitive, while field names are case sensitive.
- Stream names are not validated by PyAirbyte. If the stream name
  does not exist in the catalog, the override may be ignored.

</ApiMember>

#### `set_primary_keys` {#airbyte.sources.base.Source.set_primary_keys}

<ApiMember kind="method">

<ApiSignature>

```python
def set_primary_keys(self, **kwargs: str | list[str]) -> None
```

</ApiSignature>

Override the primary keys for one or more streams.

This does not unset previously set primary keys.

Usage:
    ```python
    source.set_primary_keys(
        stream1="pk1",
        stream2=["pk1", "pk2"],
    )
    ```

**Note:**

- This does not unset previously set primary keys.
- The primary key must be a single field name or a list of field names.
- Not all streams support overriding primary keys. If a stream does not support overriding
  primary keys, the override may be ignored.
- Stream names are case insensitive, while field names are case sensitive.
- Stream names are not validated by PyAirbyte. If the stream name
  does not exist in the catalog, the override may be ignored.

</ApiMember>

#### `set_streams` {#airbyte.sources.base.Source.set_streams}

<ApiMember kind="method">

<ApiSignature>

```python
def set_streams(self, streams: list[str]) -> None
```

</ApiSignature>

Deprecated. See select_streams().

</ApiMember>

</ApiMember>