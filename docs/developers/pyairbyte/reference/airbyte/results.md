---
sidebar_label: results
title: airbyte.results
---

Module which defines the `ReadResult` and `WriteResult` classes.

These classes are used to return information about read and write operations, respectively. They
contain information such as the number of records read or written, the cache object, and the
state handlers for a sync.

## annotations

## Mapping

## TYPE\_CHECKING

## CachedDataset

## ReadResult Objects

```python
class ReadResult(Mapping[str, CachedDataset])
```

The result of a read operation.

This class is used to return information about the read operation, such as the number of
records read. It should not be created directly, but instead returned by the write method
of a destination.

#### \_\_init\_\_

```python
def __init__(*, source_name: str, processed_streams: list[str],
             cache: CacheBase, progress_tracker: ProgressTracker) -> None
```

Initialize a read result.

This class should not be created directly. Instead, it should be returned by the `read`
method of the `Source` class.

#### \_\_getitem\_\_

```python
def __getitem__(stream: str) -> CachedDataset
```

Return the cached dataset for a given stream name.

#### \_\_contains\_\_

```python
def __contains__(stream: object) -> bool
```

Return whether a given stream name was included in processing.

#### \_\_iter\_\_

```python
def __iter__() -> Iterator[str]
```

Return an iterator over the stream names that were processed.

#### \_\_len\_\_

```python
def __len__() -> int
```

Return the number of streams that were processed.

#### get\_sql\_engine

```python
def get_sql_engine() -> Engine
```

Return the SQL engine used by the cache.

#### processed\_records

```python
@property
def processed_records() -> int
```

The total number of records read from the source.

#### streams

```python
@property
def streams() -> Mapping[str, CachedDataset]
```

Return a mapping of stream names to cached datasets.

#### cache

```python
@property
def cache() -> CacheBase
```

Return the cache object.

## WriteResult Objects

```python
class WriteResult()
```

The result of a write operation.

This class is used to return information about the write operation, such as the number of
records written. It should not be created directly, but instead returned by the write method
of a destination.

#### \_\_init\_\_

```python
def __init__(*, destination: AirbyteWriterInterface | Destination,
             source_data: Source | ReadResult,
             catalog_provider: CatalogProvider, state_writer: StateWriterBase,
             progress_tracker: ProgressTracker) -> None
```

Initialize a write result.

This class should not be created directly. Instead, it should be returned by the `write`
method of the `Destination` class.

#### processed\_records

```python
@property
def processed_records() -> int
```

The total number of records written to the destination.

#### get\_state\_provider

```python
def get_state_provider() -> StateProviderBase
```

Return the state writer as a state provider.

As a public interface, we only expose the state writer as a state provider. This is because
the state writer itself is only intended for internal use. As a state provider, the state
writer can be used to read the state artifacts that were written. This can be useful for
testing or debugging.

