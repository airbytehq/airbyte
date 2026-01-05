---
sidebar_label: base
title: airbyte.destinations.base
---

Destination base classes.

For usage examples, see the `airbyte.destinations` module documentation.

## annotations

## warnings

## IO

## TYPE\_CHECKING

## Any

## Literal

## cast

## exc

## ConnectorBase

## AirbyteMessageIterator

## as\_temp\_files

## AirbyteWriterInterface

## get\_default\_cache

## ProgressTracker

## ReadResult

## WriteResult

## CatalogProvider

## JoinedStateProvider

## StateProviderBase

## StaticInputState

## NoOpStateWriter

## StdOutStateWriter

## Source

## WriteStrategy

## Destination Objects

```python
class Destination(ConnectorBase, AirbyteWriterInterface)
```

A class representing a destination that can be called.

#### connector\_type

#### \_\_init\_\_

```python
def __init__(executor: Executor,
             name: str,
             config: dict[str, Any] | None = None,
             *,
             config_change_callback: ConfigChangeCallback | None = None,
             validate: bool = False) -> None
```

Initialize the source.

If config is provided, it will be validated against the spec if validate is True.

#### write

```python
def write(source_data: Source | ReadResult,
          *,
          streams: list[str] | Literal["*"] | None = None,
          cache: CacheBase | Literal[False] | None = None,
          state_cache: CacheBase | Literal[False] | None = None,
          write_strategy: WriteStrategy = WriteStrategy.AUTO,
          force_full_refresh: bool = False) -> WriteResult
```

Write data from source connector or already cached source data.

Caching is enabled by default, unless explicitly disabled.

**Arguments**:

- `source_data` - The source data to write. Can be a `Source` or a `ReadResult` object.
- `streams` - The streams to write to the destination. If omitted or if &quot;*&quot; is provided,
  all streams will be written. If `source_data` is a source, then streams must be
  selected here or on the source. If both are specified, this setting will override
  the stream selection on the source.
- `cache` - The cache to use for reading source_data. If `None`, no cache will be used. If
  False, the cache will be disabled. This must be `None` if `source_data` is already
  a `Cache` object.
- `Source`0 - A cache to use for storing incremental state. You do not need to set this
  if `cache` is specified or if `source_data` is a `Cache` object. Set to `Source`4 to
  disable state management.
- `Source`5 - The strategy to use for writing source_data. If `Source`6, the connector
  will decide the best strategy to use.
- `Source`7 - Whether to force a full refresh of the source_data. If `Source`8, any
  existing state will be ignored and all source data will be reloaded.
  
  For incremental syncs, `cache` or `Source`0 will be checked for matching state values.
  If the cache has tracked state, this will be used for the sync. Otherwise, if there is
  a known destination state, the destination-specific state will be used. If neither are
  available, a full refresh will be performed.

#### \_write\_airbyte\_message\_stream

```python
def _write_airbyte_message_stream(stdin: IO[str] | AirbyteMessageIterator,
                                  *,
                                  catalog_provider: CatalogProvider,
                                  write_strategy: WriteStrategy,
                                  state_writer: StateWriterBase | None = None,
                                  progress_tracker: ProgressTracker) -> None
```

Read from the connector and write to the cache.

#### \_\_all\_\_

