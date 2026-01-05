---
sidebar_label: base
title: airbyte._writers.base
---

Write interfaces for PyAirbyte.

## annotations

## abc

## IO

## TYPE\_CHECKING

## WriterRuntimeInfo

## AirbyteWriterInterface Objects

```python
class AirbyteWriterInterface(abc.ABC)
```

An interface for writing Airbyte messages.

#### name

```python
@property
def name() -> str
```

Return the name of the writer.

This is used for logging and state tracking.

#### \_get\_writer\_runtime\_info

```python
def _get_writer_runtime_info() -> WriterRuntimeInfo
```

Get metadata for telemetry and performance logging.

#### config\_hash

```python
@property
def config_hash() -> str | None
```

Return a hash of the writer configuration.

This is used for logging and state tracking.

#### \_write\_airbyte\_io\_stream

```python
def _write_airbyte_io_stream(stdin: IO[str],
                             *,
                             catalog_provider: CatalogProvider,
                             write_strategy: WriteStrategy,
                             state_writer: StateWriterBase | None = None,
                             progress_tracker: ProgressTracker) -> None
```

Read from the connector and write to the cache.

This is a specialized version of `_write_airbyte_message_stream` that reads from an IO
stream. Writers can override this method to provide custom behavior for reading from an IO
stream, without paying the cost of converting the stream to an AirbyteMessageIterator.

#### \_write\_airbyte\_message\_stream

```python
@abc.abstractmethod
def _write_airbyte_message_stream(stdin: IO[str] | AirbyteMessageIterator,
                                  *,
                                  catalog_provider: CatalogProvider,
                                  write_strategy: WriteStrategy,
                                  state_writer: StateWriterBase | None = None,
                                  progress_tracker: ProgressTracker) -> None
```

Write the incoming data.

Note: Callers should use `_write_airbyte_io_stream` instead of this method if
`stdin` is always an IO stream. This ensures that the most efficient method is used for
writing the incoming stream.

