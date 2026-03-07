---
id: airbyte-datasets-index
title: airbyte.datasets.index
---

Module airbyte.datasets
=======================
PyAirbyte dataset classes.

Classes
-------

`CachedDataset(cache: CacheBase, stream_name: str, stream_configuration: ConfiguredAirbyteStream | Literal[False] | None = None)`
:   A dataset backed by a SQL table cache.
    
    Because this dataset includes all records from the underlying table, we also expose the
    underlying table as a SQLAlchemy Table object.
    
    We construct the query statement by selecting all columns from the table.
    
    This prevents the need to scan the table schema to construct the query statement.
    
    If stream_configuration is None, we attempt to retrieve the stream configuration from the
    cache processor. This is useful when constructing a dataset from a CachedDataset object,
    which already has the stream configuration.
    
    If stream_configuration is set to False, we skip the stream configuration retrieval.

    ### Ancestors (in MRO)

    * airbyte.datasets._sql.SQLDataset
    * airbyte.datasets._base.DatasetBase
    * abc.ABC

    ### Methods

    `to_arrow(self, *, max_chunk_size: int = 100000) ‑> Dataset`
    :   Return an Arrow Dataset containing the data from the specified stream.
        
        Args:
            stream_name (str): Name of the stream to retrieve data from.
            max_chunk_size (int): max number of records to include in each batch of pyarrow dataset.
        
        Returns:
            pa.dataset.Dataset: Arrow Dataset containing the stream's data.

    `to_pandas(self) ‑> DataFrame`
    :   Return the underlying dataset data as a pandas DataFrame.

    `to_sql_table(self) ‑> Table`
    :   Return the underlying SQL table as a SQLAlchemy Table object.

`DatasetBase(stream_metadata: ConfiguredAirbyteStream)`
:   Base implementation for all datasets.

    ### Ancestors (in MRO)

    * abc.ABC

    ### Descendants

    * airbyte.datasets._inmemory.InMemoryDataset
    * airbyte.datasets._lazy.LazyDataset
    * airbyte.datasets._sql.SQLDataset

    ### Instance variables

    `column_names: list[str]`
    :   Return the list of top-level column names.

    ### Methods

    `to_arrow(self, *, max_chunk_size: int = 100000) ‑> Dataset`
    :   Return an Arrow Dataset representation of the dataset.
        
        This method should be implemented by subclasses.

    `to_documents(self, title_property: str | None = None, content_properties: list[str] | None = None, metadata_properties: list[str] | None = None, *, render_metadata: bool = False) ‑> Iterable[Document]`
    :   Return the iterator of documents.
        
        If metadata_properties is not set, all properties that are not content will be added to
        the metadata.
        
        If render_metadata is True, metadata will be rendered in the document, as well as the
        the main content. Otherwise, metadata will be attached to the document but not rendered.

    `to_pandas(self) ‑> pandas.core.frame.DataFrame`
    :   Return a pandas DataFrame representation of the dataset.
        
        The base implementation simply passes the record iterator to Panda's DataFrame constructor.

`DatasetMap()`
:   A generic interface for a set of streams or datasets.

    ### Ancestors (in MRO)

    * collections.abc.Mapping
    * collections.abc.Collection
    * collections.abc.Sized
    * collections.abc.Iterable
    * collections.abc.Container

`LazyDataset(iterator: Iterator[dict[str, Any]], *, stream_metadata: ConfiguredAirbyteStream, stop_event: threading.Event | None, progress_tracker: progress.ProgressTracker)`
:   A dataset that is loaded incrementally from a source or a SQL query.

    ### Ancestors (in MRO)

    * airbyte.datasets._base.DatasetBase
    * abc.ABC

    ### Methods

    `close(self) ‑> None`
    :   Stop the dataset iterator.
        
        This method is used to signal the dataset to stop fetching records, for example
        when the dataset is being fetched incrementally and the user wants to stop the
        fetching process.

    `fetch_all(self) ‑> airbyte.datasets._inmemory.InMemoryDataset`
    :   Fetch all records to memory and return an InMemoryDataset.

`SQLDataset(cache: CacheBase, stream_name: str, query_statement: Select, stream_configuration: ConfiguredAirbyteStream | Literal[False] | None = None)`
:   A dataset that is loaded incrementally from a SQL query.
    
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

    ### Ancestors (in MRO)

    * airbyte.datasets._base.DatasetBase
    * abc.ABC

    ### Descendants

    * airbyte.datasets._sql.CachedDataset

    ### Instance variables

    `column_names: list[str]`
    :   Return the list of top-level column names, including internal Airbyte columns.

    `stream_name: str`
    :

    ### Methods

    `to_arrow(self, *, max_chunk_size: int = 100000) ‑> Dataset`
    :   Return an Arrow Dataset representation of the dataset.
        
        This method should be implemented by subclasses.

    `to_pandas(self) ‑> DataFrame`
    :   Return a pandas DataFrame representation of the dataset.
        
        The base implementation simply passes the record iterator to Panda's DataFrame constructor.

    `with_filter(self, *filter_expressions: ClauseElement | str) ‑> SQLDataset`
    :   Filter the dataset by a set of column values.
        
        Filters can be specified as either a string or a SQLAlchemy expression.
        
        Filters are lazily applied to the dataset, so they can be chained together. For example:
        
                dataset.with_filter("id > 5").with_filter("id < 10")
        
        is equivalent to:
        
                dataset.with_filter("id > 5", "id < 10")