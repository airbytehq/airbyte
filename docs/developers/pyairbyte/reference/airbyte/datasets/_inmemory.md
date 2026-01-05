---
sidebar_label: _inmemory
title: airbyte.datasets._inmemory
---

In-memory dataset class.

## annotations

## TYPE\_CHECKING

## Any

## overrides

## DatasetBase

## InMemoryDataset Objects

```python
class InMemoryDataset(DatasetBase)
```

A dataset that is held in memory.

This dataset is useful for testing and debugging purposes, but should not be used with any
large datasets.

#### \_\_init\_\_

```python
def __init__(records: list[dict[str, Any]],
             stream_metadata: ConfiguredAirbyteStream) -> None
```

Initialize the dataset with a list of records.

#### \_\_iter\_\_

```python
@overrides
def __iter__() -> Iterator[dict[str, Any]]
```

Return the iterator of records.

#### \_\_len\_\_

```python
def __len__() -> int
```

Return the number of records in the dataset.

