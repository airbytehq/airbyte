---
sidebar_label: _map
title: airbyte.datasets._map
---

A generic interface for a set of streams.

TODO: This is a work in progress. It is not yet used by any other code.
TODO: Implement before release, or delete.

## annotations

## Iterator

## Mapping

## TYPE\_CHECKING

## DatasetMap Objects

```python
class DatasetMap(Mapping)
```

A generic interface for a set of streams or datasets.

#### \_\_init\_\_

```python
def __init__() -> None
```

#### \_\_getitem\_\_

```python
def __getitem__(key: str) -> DatasetBase
```

#### \_\_iter\_\_

```python
def __iter__() -> Iterator[str]
```

#### \_\_len\_\_

```python
def __len__() -> int
```

