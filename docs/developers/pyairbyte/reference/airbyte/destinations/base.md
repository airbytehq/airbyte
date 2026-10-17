---
id: airbyte-destinations-base
title: "airbyte.destinations.base Module"
sidebar_label: "airbyte.destinations.base"
toc_max_heading_level: 5
---

# `airbyte.destinations.base` Module

Destination base classes.

For usage examples, see the `airbyte.destinations` module documentation.

### `Destination` {#airbyte.destinations.base.Destination}

<ApiMember kind="class">

<ApiSignature>

```python
class Destination(
    executor: Executor,
    name: str,
    config: dict[str, Any] | None = None,
    *,
    config_change_callback: ConfigChangeCallback | None = None,
    validate: bool = False,
)
```

</ApiSignature>

A class representing a destination that can be called.

Initialize the source.

If config is provided, it will be validated against the spec if validate is True.

#### Bases {#airbyte.destinations.base.Destination--bases}

`airbyte._connector_base.ConnectorBase`, `airbyte._writers.base.AirbyteWriterInterface`
#### Class Variables {#airbyte.destinations.base.Destination--class-variables}

- **`connector_type`**&nbsp;(`Literal['destination', 'source']`)

#### Instance Variables {#airbyte.destinations.base.Destination--instance-variables}

- **`is_cache_supported`**&nbsp;(`bool`)

  Whether this destination has a compatible cache implementation.

  Returns `True` when `get_sql_cache()` is expected to succeed for
  the destination's connector type.

#### Methods {#airbyte.destinations.base.Destination--methods}

##### `get_sql_cache` {#airbyte.destinations.base.Destination.get_sql_cache}

<ApiMember kind="method">

<ApiSignature>

```python
def get_sql_cache(self, *, schema_name: str | None = None) -> CacheBase
```

</ApiSignature>

Return a SQL Cache for querying data written by this destination.

This follows the same pattern as
`SyncResult.get_sql_cache()` in `airbyte.cloud.sync_results`:
it builds a cache from the destination's configuration using
`destination_to_cache()`.

**Args:**

- **`schema_name`**: Override the schema/namespace on the returned cache. When `None` the cache uses the default schema from the destination config.

**Raises:**

- **`ValueError`**: If the destination type is not supported.

</ApiMember>

##### `write` {#airbyte.destinations.base.Destination.write}

<ApiMember kind="method">

<ApiSignature>

```python
def write(
    self,
    source_data: Source | ReadResult,
    *,
    streams: "list[str] | Literal['*'] | None" = None,
    cache: CacheBase | Literal[False] | None = None,
    state_cache: CacheBase | Literal[False] | None = None,
    write_strategy: WriteStrategy = WriteStrategy.AUTO,
    force_full_refresh: bool = False,
) -> WriteResult
```

</ApiSignature>

Write data from source connector or already cached source data.

Caching is enabled by default, unless explicitly disabled.

**Args:**

- **`source_data`**: The source data to write. Can be a `Source` or a `ReadResult` object.
- **`streams`**: The streams to write to the destination. If omitted or if "*" is provided, all streams will be written. If `source_data` is a source, then streams must be selected here or on the source. If both are specified, this setting will override the stream selection on the source.
- **`cache`**: The cache to use for reading source_data. If `None`, no cache will be used. If False, the cache will be disabled. This must be `None` if `source_data` is already a `Cache` object.
- **`state_cache`**: A cache to use for storing incremental state. You do not need to set this if `cache` is specified or if `source_data` is a `Cache` object. Set to `False` to disable state management.
- **`write_strategy`**: The strategy to use for writing source_data. If `AUTO`, the connector will decide the best strategy to use.
- **`force_full_refresh`**: Whether to force a full refresh of the source_data. If `True`, any existing state will be ignored and all source data will be reloaded.

For incremental syncs, `cache` or `state_cache` will be checked for matching state values.
If the cache has tracked state, this will be used for the sync. Otherwise, if there is
a known destination state, the destination-specific state will be used. If neither are
available, a full refresh will be performed.

</ApiMember>

</ApiMember>