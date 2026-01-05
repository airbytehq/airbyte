---
sidebar_label: file_writers
title: airbyte._writers.file_writers
---

Abstract base class for File Writers, which write and read from file storage.

## annotations

## abc

## defaultdict

## Path

## IO

## TYPE\_CHECKING

## final

## ulid

## exc

## progress

## BatchHandle

## LowerCaseNormalizer

## AirbyteWriterInterface

## StreamRecord

## StreamRecordHandler

#### DEFAULT\_BATCH\_SIZE

## FileWriterBase Objects

```python
class FileWriterBase(AirbyteWriterInterface)
```

A generic abstract implementation for a file-based writer.

#### default\_cache\_file\_suffix

#### prune\_extra\_fields

#### MAX\_BATCH\_SIZE

#### \_\_init\_\_

```python
def __init__(cache_dir: Path, *, cleanup: bool = True) -> None
```

Initialize the file writer.

#### \_get\_new\_cache\_file\_path

```python
def _get_new_cache_file_path(stream_name: str,
                             batch_id: str | None = None) -> Path
```

Return a new cache file path for the given stream.

#### \_open\_new\_file

```python
def _open_new_file(file_path: Path) -> IO[str]
```

Open a new file for writing.

#### \_flush\_active\_batch

```python
def _flush_active_batch(stream_name: str,
                        progress_tracker: ProgressTracker) -> None
```

Flush the active batch for the given stream.

This entails moving the active batch to the pending batches, closing any open files, and
logging the batch as written.

#### \_new\_batch

```python
def _new_batch(stream_name: str,
               progress_tracker: progress.ProgressTracker) -> BatchHandle
```

Create and return a new batch handle.

The base implementation creates and opens a new file for writing so it is ready to receive
records.

This also flushes the active batch if one already exists for the given stream.

#### \_close\_batch

```python
def _close_batch(batch_handle: BatchHandle) -> None
```

Close the current batch.

#### cleanup\_all

```python
@final
def cleanup_all() -> None
```

Clean up the cache.

For file writers, this means deleting the files created and declared in the batch.

This method is final because it should not be overridden.

Subclasses should override `_cleanup_batch` instead.

#### process\_record\_message

```python
def process_record_message(record_msg: AirbyteRecordMessage,
                           stream_record_handler: StreamRecordHandler,
                           progress_tracker: progress.ProgressTracker) -> None
```

Write a record to the cache.

This method is called for each record message, before the batch is written.

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

This is not implemented for file writers, as they should be wrapped by another writer that
handles state tracking and other logic.

#### flush\_active\_batches

```python
def flush_active_batches(progress_tracker: ProgressTracker) -> None
```

Flush active batches for all streams.

#### \_cleanup\_batch

```python
def _cleanup_batch(batch_handle: BatchHandle) -> None
```

Clean up the cache.

For file writers, this means deleting the files created and declared in the batch.

This method is a no-op if the `cleanup` config option is set to False.

#### \_new\_batch\_id

```python
def _new_batch_id() -> str
```

Return a new batch handle.

#### \_\_del\_\_

```python
@final
def __del__() -> None
```

Teardown temporary resources when instance is unloaded from memory.

#### \_write\_record\_dict

```python
@abc.abstractmethod
def _write_record_dict(record_dict: StreamRecord,
                       open_file_writer: IO[str]) -> None
```

Write one record to a file.

#### get\_active\_batch

```python
def get_active_batch(stream_name: str) -> BatchHandle | None
```

Return the active batch for a specific stream name.

#### get\_pending\_batches

```python
def get_pending_batches(stream_name: str) -> list[BatchHandle]
```

Return the pending batches for a specific stream name.

#### get\_finalized\_batches

```python
def get_finalized_batches(stream_name: str) -> list[BatchHandle]
```

Return the finalized batches for a specific stream name.

