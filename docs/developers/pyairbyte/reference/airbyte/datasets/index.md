---
id: airbyte-datasets-index
title: airbyte.datasets.index
---

PyAirbyte dataset classes.

### `CachedDataset` {#airbyte.datasets.CachedDataset}

<ApiMember kind="class">

<ApiSignature>

```python
class CachedDataset(
    cache: CacheBase,
    stream_name: str,
    stream_configuration: ConfiguredAirbyteStream | Literal[False] | None = None,
)
```

</ApiSignature>

A dataset backed by a SQL table cache.

Because this dataset includes all records from the underlying table, we also expose the
underlying table as a SQLAlchemy Table object.

We construct the query statement by selecting all columns from the table.

This prevents the need to scan the table schema to construct the query statement.

If stream_configuration is None, we attempt to retrieve the stream configuration from the
cache processor. This is useful when constructing a dataset from a CachedDataset object,
which already has the stream configuration.

If stream_configuration is set to False, we skip the stream configuration retrieval.

**Bases:** `airbyte.datasets._sql.SQLDataset`, `airbyte.datasets._base.DatasetBase`, `abc.ABC`

#### `to_arrow` {#airbyte.datasets.CachedDataset.to_arrow}

<ApiMember kind="method">

<ApiSignature>

```python
def to_arrow(self, *, max_chunk_size: int = 100000) -> Dataset
```

</ApiSignature>

Return an Arrow Dataset containing the data from the specified stream.

**Args:**

- **`stream_name` (*str*)**: Name of the stream to retrieve data from.
- **`max_chunk_size` (*int*)**: max number of records to include in each batch of pyarrow dataset.

**Returns:**

- **`pa.dataset.Dataset`**: Arrow Dataset containing the stream's data.

</ApiMember>

#### `to_pandas` {#airbyte.datasets.CachedDataset.to_pandas}

<ApiMember kind="method">

<ApiSignature>

```python
def to_pandas(self) -> DataFrame
```

</ApiSignature>

Return the underlying dataset data as a pandas DataFrame.

</ApiMember>

#### `to_sql_table` {#airbyte.datasets.CachedDataset.to_sql_table}

<ApiMember kind="method">

<ApiSignature>

```python
def to_sql_table(self) -> Table
```

</ApiSignature>

Return the underlying SQL table as a SQLAlchemy Table object.

</ApiMember>

</ApiMember>

### `DatasetBase` {#airbyte.datasets.DatasetBase}

<ApiMember kind="class">

<ApiSignature>

```python
class DatasetBase(stream_metadata: ConfiguredAirbyteStream)
```

</ApiSignature>

Base implementation for all datasets.

**Bases:** `abc.ABC`

**Subclasses:** `airbyte.datasets._inmemory.InMemoryDataset`, `airbyte.datasets._lazy.LazyDataset`, `airbyte.datasets._sql.SQLDataset`

#### Attributes {#airbyte.datasets.DatasetBase--attributes}

- **`column_names`**&nbsp;(`list[str]`)

  Return the list of top-level column names.

#### `to_arrow` {#airbyte.datasets.DatasetBase.to_arrow}

<ApiMember kind="method">

<ApiSignature>

```python
def to_arrow(self, *, max_chunk_size: int = 100000) -> Dataset
```

</ApiSignature>

Return an Arrow Dataset representation of the dataset.

This method should be implemented by subclasses.

</ApiMember>

#### `to_documents` {#airbyte.datasets.DatasetBase.to_documents}

<ApiMember kind="method">

<ApiSignature>

```python
def to_documents(
    self,
    title_property: str | None = None,
    content_properties: list[str] | None = None,
    metadata_properties: list[str] | None = None,
    *,
    render_metadata: bool = False,
) -> Iterable[Document]
```

</ApiSignature>

Return the iterator of documents.

If metadata_properties is not set, all properties that are not content will be added to
the metadata.

If render_metadata is True, metadata will be rendered in the document, as well as the
the main content. Otherwise, metadata will be attached to the document but not rendered.

</ApiMember>

#### `to_pandas` {#airbyte.datasets.DatasetBase.to_pandas}

<ApiMember kind="method">

<ApiSignature>

```python
def to_pandas(self) -> pandas.core.frame.DataFrame
```

</ApiSignature>

Return a pandas DataFrame representation of the dataset.

The base implementation simply passes the record iterator to Panda's DataFrame constructor.

</ApiMember>

</ApiMember>

### `DatasetMap` {#airbyte.datasets.DatasetMap}

<ApiMember kind="class">

<ApiSignature>

```python
class DatasetMap()
```

</ApiSignature>

A generic interface for a set of streams or datasets.

**Bases:** `collections.abc.Mapping`, `collections.abc.Collection`, `collections.abc.Sized`, `collections.abc.Iterable`, `collections.abc.Container`

</ApiMember>

### `LazyDataset` {#airbyte.datasets.LazyDataset}

<ApiMember kind="class">

<ApiSignature>

```python
class LazyDataset(
    iterator: Iterator[dict[str, Any]],
    *,
    stream_metadata: ConfiguredAirbyteStream,
    stop_event: threading.Event | None,
    progress_tracker: progress.ProgressTracker,
)
```

</ApiSignature>

A dataset that is loaded incrementally from a source or a SQL query.

**Bases:** `airbyte.datasets._base.DatasetBase`, `abc.ABC`

#### `close` {#airbyte.datasets.LazyDataset.close}

<ApiMember kind="method">

<ApiSignature>

```python
def close(self) -> None
```

</ApiSignature>

Stop the dataset iterator.

This method is used to signal the dataset to stop fetching records, for example
when the dataset is being fetched incrementally and the user wants to stop the
fetching process.

</ApiMember>

#### `fetch_all` {#airbyte.datasets.LazyDataset.fetch_all}

<ApiMember kind="method">

<ApiSignature>

```python
def fetch_all(self) -> airbyte.datasets._inmemory.InMemoryDataset
```

</ApiSignature>

Fetch all records to memory and return an InMemoryDataset.

</ApiMember>

</ApiMember>

### `SQLDataset` {#airbyte.datasets.SQLDataset}

<ApiMember kind="class">

<ApiSignature>

```python
class SQLDataset(
    cache: CacheBase,
    stream_name: str,
    query_statement: Select,
    stream_configuration: ConfiguredAirbyteStream | Literal[False] | None = None,
)
```

</ApiSignature>

A dataset that is loaded incrementally from a SQL query.

The CachedDataset class is a subclass of this class, which simply passes a SELECT over the full
table as the query statement.

Initialize the dataset with a cache, stream name, and query statement.

This class is not intended to be created directly. Instead, you can retrieve
datasets from caches or Cloud connection objects, etc.

The query statement should be a SQLAlchemy Selectable object that can be executed to
retrieve records from the dataset.

If stream_configuration is not provided, we attempt to retrieve the stream configuration
from the cache processor. This is useful when constructing a dataset from a CachedDataset
object, which already has the stream configuration.

If stream_configuration is set to False, we skip the stream configuration retrieval.

**Bases:** `airbyte.datasets._base.DatasetBase`, `abc.ABC`

**Subclasses:** `airbyte.datasets._sql.CachedDataset`

#### Attributes {#airbyte.datasets.SQLDataset--attributes}

- **`column_names`**&nbsp;(`list[str]`)

  Return the list of top-level column names, including internal Airbyte columns.

- **`stream_name`**&nbsp;(`str`)

#### `to_arrow` {#airbyte.datasets.SQLDataset.to_arrow}

<ApiMember kind="method">

<ApiSignature>

```python
def to_arrow(self, *, max_chunk_size: int = 100000) -> Dataset
```

</ApiSignature>

Return an Arrow Dataset representation of the dataset.

This method should be implemented by subclasses.

</ApiMember>

#### `to_pandas` {#airbyte.datasets.SQLDataset.to_pandas}

<ApiMember kind="method">

<ApiSignature>

```python
def to_pandas(self) -> DataFrame
```

</ApiSignature>

Return a pandas DataFrame representation of the dataset.

The base implementation simply passes the record iterator to Panda's DataFrame constructor.

</ApiMember>

#### `with_filter` {#airbyte.datasets.SQLDataset.with_filter}

<ApiMember kind="method">

<ApiSignature>

```python
def with_filter(self, *filter_expressions: ClauseElement | str) -> SQLDataset
```

</ApiSignature>

Filter the dataset by a set of column values.

Filters can be specified as either a string or a SQLAlchemy expression.

Filters are lazily applied to the dataset, so they can be chained together. For example:

        dataset.with_filter("id > 5").with_filter("id < 10")

is equivalent to:

        dataset.with_filter("id > 5", "id < 10")

</ApiMember>

</ApiMember>