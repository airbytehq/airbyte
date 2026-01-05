---
sidebar_label: _lazy
title: airbyte.datasets._lazy
---

## annotations

## TYPE\_CHECKING

## Any

## overrides

## DatasetBase

## InMemoryDataset

## LazyDataset Objects

```python
class LazyDataset(DatasetBase)
```

A dataset that is loaded incrementally from a source or a SQL query.

#### \_\_init\_\_

```python
def __init__(iterator: Iterator[dict[str, Any]], *,
             stream_metadata: ConfiguredAirbyteStream,
             stop_event: threading.Event | None,
             progress_tracker: progress.ProgressTracker) -> None
```

#### \_\_iter\_\_

```python
@overrides
def __iter__() -> Iterator[dict[str, Any]]
```

#### \_\_next\_\_

```python
def __next__() -> Mapping[str, Any]
```

#### fetch\_all

```python
def fetch_all() -> InMemoryDataset
```

Fetch all records to memory and return an InMemoryDataset.

#### close

```python
def close() -> None
```

Stop the dataset iterator.

This method is used to signal the dataset to stop fetching records, for example
when the dataset is being fetched incrementally and the user wants to stop the
fetching process.

#### \_\_del\_\_

```python
def __del__() -> None
```

Close the dataset when the object is deleted.

