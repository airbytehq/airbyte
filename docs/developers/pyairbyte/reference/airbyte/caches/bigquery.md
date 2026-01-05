---
sidebar_label: bigquery
title: airbyte.caches.bigquery
---

A BigQuery implementation of the cache.

## Usage Example

```python
import airbyte as ab
from airbyte.caches import BigQueryCache

cache = BigQueryCache(
    project_name="myproject",
    dataset_name="mydataset",
    credentials_path="path/to/credentials.json",
)
```

## annotations

## TYPE\_CHECKING

## ClassVar

## NoReturn

## DestinationBigquery

## BigQueryConfig

## BigQuerySqlProcessor

## CacheBase

## DEFAULT\_ARROW\_MAX\_CHUNK\_SIZE

## bigquery\_cache\_to\_destination\_configuration

## BigQueryCache Objects

```python
class BigQueryCache(BigQueryConfig, CacheBase)
```

The BigQuery cache implementation.

#### \_sql\_processor\_class

#### paired\_destination\_name

#### paired\_destination\_config\_class

#### paired\_destination\_config

```python
@property
def paired_destination_config() -> DestinationBigquery
```

Return a dictionary of destination configuration values.

#### get\_arrow\_dataset

```python
def get_arrow_dataset(
        stream_name: str,
        *,
        max_chunk_size: int = DEFAULT_ARROW_MAX_CHUNK_SIZE) -> NoReturn
```

Raises NotImplementedError; BigQuery doesn&#x27;t support `pd.read_sql_table`.

See: https://github.com/airbytehq/PyAirbyte/issues/165

#### \_\_all\_\_

