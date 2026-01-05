---
sidebar_label: _sql
title: airbyte.datasets._sql
---

SQL datasets class.

## annotations

## warnings

## TYPE\_CHECKING

## Any

## Literal

## cast

## overrides

## and\_

## func

## select

## text

## ConfiguredAirbyteStream

## AB\_EXTRACTED\_AT\_COLUMN

## AB\_META\_COLUMN

## AB\_RAW\_ID\_COLUMN

## DEFAULT\_ARROW\_MAX\_CHUNK\_SIZE

## DatasetBase

## SQLDataset Objects

```python
class SQLDataset(DatasetBase)
```

A dataset that is loaded incrementally from a SQL query.

The CachedDataset class is a subclass of this class, which simply passes a SELECT over the full
table as the query statement.

#### \_\_init\_\_

```python
def __init__(
    cache: CacheBase,
    stream_name: str,
    query_statement: Select,
    stream_configuration: ConfiguredAirbyteStream | Literal[False]
    | None = None
) -> None
```

Initialize the dataset with a cache, stream name, and query statement.

This class is not intended to be created directly. Instead, you can retrieve
datasets from caches or Cloud connection objects, etc.

The query statement should be a SQLAlchemy Selectable object that can be executed to
retrieve records from the dataset.

If stream_configuration is not provided, we attempt to retrieve the stream configuration
from the cache processor. This is useful when constructing a dataset from a CachedDataset
object, which already has the stream configuration.

If stream_configuration is set to False, we skip the stream configuration retrieval.

#### stream\_name

```python
@property
def stream_name() -> str
```

#### \_\_iter\_\_

```python
def __iter__() -> Iterator[dict[str, Any]]
```

#### \_\_len\_\_

```python
def __len__() -> int
```

Return the number of records in the dataset.

This method caches the length of the dataset after the first call.

#### to\_pandas

```python
def to_pandas() -> DataFrame
```

#### to\_arrow

```python
def to_arrow(*, max_chunk_size: int = DEFAULT_ARROW_MAX_CHUNK_SIZE) -> Dataset
```

#### with\_filter

```python
def with_filter(*filter_expressions: ClauseElement | str) -> SQLDataset
```

Filter the dataset by a set of column values.

Filters can be specified as either a string or a SQLAlchemy expression.

Filters are lazily applied to the dataset, so they can be chained together. For example:

        dataset.with_filter(&quot;id &gt; 5&quot;).with_filter(&quot;id &lt; 10&quot;)

is equivalent to:

        dataset.with_filter(&quot;id &gt; 5&quot;, &quot;id &lt; 10&quot;)

#### column\_names

```python
@property
def column_names() -> list[str]
```

Return the list of top-level column names, including internal Airbyte columns.

## CachedDataset Objects

```python
class CachedDataset(SQLDataset)
```

A dataset backed by a SQL table cache.

Because this dataset includes all records from the underlying table, we also expose the
underlying table as a SQLAlchemy Table object.

#### \_\_init\_\_

```python
def __init__(
    cache: CacheBase,
    stream_name: str,
    stream_configuration: ConfiguredAirbyteStream | Literal[False]
    | None = None
) -> None
```

We construct the query statement by selecting all columns from the table.

This prevents the need to scan the table schema to construct the query statement.

If stream_configuration is None, we attempt to retrieve the stream configuration from the
cache processor. This is useful when constructing a dataset from a CachedDataset object,
which already has the stream configuration.

If stream_configuration is set to False, we skip the stream configuration retrieval.

#### to\_pandas

```python
@overrides
def to_pandas() -> DataFrame
```

Return the underlying dataset data as a pandas DataFrame.

#### to\_arrow

```python
@overrides
def to_arrow(*, max_chunk_size: int = DEFAULT_ARROW_MAX_CHUNK_SIZE) -> Dataset
```

Return an Arrow Dataset containing the data from the specified stream.

**Arguments**:

- `stream_name` _str_ - Name of the stream to retrieve data from.
- `max_chunk_size` _int_ - max number of records to include in each batch of pyarrow dataset.
  

**Returns**:

- `pa.dataset.Dataset` - Arrow Dataset containing the stream&#x27;s data.

#### to\_sql\_table

```python
def to_sql_table() -> Table
```

Return the underlying SQL table as a SQLAlchemy Table object.

#### \_\_eq\_\_

```python
def __eq__(value: object) -> bool
```

Return True if the value is a CachedDataset with the same cache and stream name.

In the case of CachedDataset objects, we can simply compare the cache and stream name.

Note that this equality check is only supported on CachedDataset objects and not for
the base SQLDataset implementation. This is because of the complexity and computational
cost of comparing two arbitrary SQL queries that could be bound to different variables,
as well as the chance that two queries can be syntactically equivalent without being
text-wise equivalent.

#### \_\_hash\_\_

```python
def __hash__() -> int
```

