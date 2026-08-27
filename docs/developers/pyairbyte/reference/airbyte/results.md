---
id: airbyte-results
title: "airbyte.results Module"
sidebar_label: "airbyte.results"
toc_max_heading_level: 5
---

# `airbyte.results` Module

Module which defines the `ReadResult` and `WriteResult` classes.

These classes are used to return information about read and write operations, respectively. They
contain information such as the number of records read or written, the cache object, and the
state handlers for a sync.

### `ReadResult` {#airbyte.results.ReadResult}

<ApiMember kind="class">

<ApiSignature>

```python
class ReadResult(
    *,
    source_name: str,
    processed_streams: list[str],
    cache: CacheBase,
    progress_tracker: ProgressTracker,
)
```

</ApiSignature>

The result of a read operation.

This class is used to return information about the read operation, such as the number of
records read. It should not be created directly, but instead returned by the write method
of a destination.

Initialize a read result.

This class should not be created directly. Instead, it should be returned by the `read`
method of the `Source` class.

#### Bases {#airbyte.results.ReadResult--bases}

`collections.abc.Mapping`
#### Instance Variables {#airbyte.results.ReadResult--instance-variables}

- **`cache`**&nbsp;(`CacheBase`)

  Return the cache object.

- **`processed_records`**&nbsp;(`int`)

  The total number of records read from the source.

- **`streams`**&nbsp;(`Mapping[str, CachedDataset]`)

  Return a mapping of stream names to cached datasets.

#### Methods {#airbyte.results.ReadResult--methods}

#### `get_sql_engine` {#airbyte.results.ReadResult.get_sql_engine}

<ApiMember kind="method">

<ApiSignature>

```python
def get_sql_engine(self) -> Engine
```

</ApiSignature>

Return the SQL engine used by the cache.

</ApiMember>

</ApiMember>

### `WriteResult` {#airbyte.results.WriteResult}

<ApiMember kind="class">

<ApiSignature>

```python
class WriteResult(
    *,
    destination: AirbyteWriterInterface | Destination,
    source_data: Source | ReadResult,
    catalog_provider: CatalogProvider,
    state_writer: StateWriterBase,
    progress_tracker: ProgressTracker,
)
```

</ApiSignature>

The result of a write operation.

This class is used to return information about the write operation, such as the number of
records written. It should not be created directly, but instead returned by the write method
of a destination.

Initialize a write result.

This class should not be created directly. Instead, it should be returned by the `write`
method of the `Destination` class.

#### Instance Variables {#airbyte.results.WriteResult--instance-variables}

- **`processed_records`**&nbsp;(`int`)

  The total number of records written to the destination.

#### Methods {#airbyte.results.WriteResult--methods}

#### `get_state_provider` {#airbyte.results.WriteResult.get_state_provider}

<ApiMember kind="method">

<ApiSignature>

```python
def get_state_provider(self) -> StateProviderBase
```

</ApiSignature>

Return the state writer as a state provider.

As a public interface, we only expose the state writer as a state provider. This is because
the state writer itself is only intended for internal use. As a state provider, the state
writer can be used to read the state artifacts that were written. This can be useful for
testing or debugging.

</ApiMember>

</ApiMember>