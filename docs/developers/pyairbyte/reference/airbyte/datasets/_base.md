---
sidebar_label: _base
title: airbyte.datasets._base
---

## annotations

## ABC

## abstractmethod

## TYPE\_CHECKING

## Any

## cast

## DataFrame

## ConfiguredAirbyteStream

## DocumentRenderer

## DEFAULT\_ARROW\_MAX\_CHUNK\_SIZE

## DatasetBase Objects

```python
class DatasetBase(ABC)
```

Base implementation for all datasets.

#### \_\_init\_\_

```python
def __init__(stream_metadata: ConfiguredAirbyteStream) -> None
```

#### \_\_iter\_\_

```python
@abstractmethod
def __iter__() -> Iterator[dict[str, Any]]
```

Return the iterator of records.

#### to\_pandas

```python
def to_pandas() -> DataFrame
```

Return a pandas DataFrame representation of the dataset.

The base implementation simply passes the record iterator to Panda&#x27;s DataFrame constructor.

#### to\_arrow

```python
def to_arrow(*, max_chunk_size: int = DEFAULT_ARROW_MAX_CHUNK_SIZE) -> Dataset
```

Return an Arrow Dataset representation of the dataset.

This method should be implemented by subclasses.

#### to\_documents

```python
def to_documents(title_property: str | None = None,
                 content_properties: list[str] | None = None,
                 metadata_properties: list[str] | None = None,
                 *,
                 render_metadata: bool = False) -> Iterable[Document]
```

Return the iterator of documents.

If metadata_properties is not set, all properties that are not content will be added to
the metadata.

If render_metadata is True, metadata will be rendered in the document, as well as the
the main content. Otherwise, metadata will be attached to the document but not rendered.

#### column\_names

```python
@property
def column_names() -> list[str]
```

Return the list of top-level column names.

