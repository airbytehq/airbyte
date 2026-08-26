---
id: airbyte-caches-bigquery
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

### `BigQueryCache` {#airbyte.caches.bigquery.BigQueryCache}

<ApiMember kind="class">

<ApiSignature>

```python
class BigQueryCache(**data: Any)
```

</ApiSignature>

The BigQuery cache implementation.

Initialize the cache and backends.

**Bases:** `airbyte._processors.sql.bigquery.BigQueryConfig`, `airbyte.caches.base.CacheBase`, `airbyte.shared.sql_processor.SqlConfig`, `airbyte._writers.base.AirbyteWriterInterface`, `abc.ABC`

#### Attributes {#airbyte.caches.bigquery.BigQueryCache--attributes}

- **`paired_destination_config_class`**&nbsp;(`ClassVar[type | None]`)

  DestinationBigquery(dataset_id: 'str', dataset_location: 'DatasetLocation', project_id: 'str', cdc_deletion_mode: 'Optional[CDCDeletionMode]' = &lt;CDCDeletionMode.HARD_DELETE: 'Hard delete'&gt;, credentials_json: 'Optional[str]' = None, DESTINATION_TYPE: 'Final[Bigquery]' = &lt;Bigquery.BIGQUERY: 'bigquery'&gt;, disable_type_dedupe: 'Optional[bool]' = False, loading_method: 'Optional[LoadingMethod]' = None, raw_data_dataset: 'Optional[str]' = None)

- **`paired_destination_name`**&nbsp;(`ClassVar[str | None]`)

#### `get_arrow_dataset` {#airbyte.caches.bigquery.BigQueryCache.get_arrow_dataset}

<ApiMember kind="method">

<ApiSignature>

```python
def get_arrow_dataset(
    self,
    stream_name: str,
    *,
    max_chunk_size: int = 100000,
) -> NoReturn
```

</ApiSignature>

Raises NotImplementedError; BigQuery doesn't support `pd.read_sql_table`.

See: https://github.com/airbytehq/PyAirbyte/issues/165

</ApiMember>

</ApiMember>

### `BigQueryConfig` {#airbyte.caches.bigquery.BigQueryConfig}

<ApiMember kind="class">

<ApiSignature>

```python
class BigQueryConfig(**data: Any)
```

</ApiSignature>

Configuration for BigQuery.

Raises ``ValidationError`` if the input data cannot be
validated to form a valid model.

`self` is explicitly positional-only to allow `self` as a field name.

**Bases:** `airbyte.shared.sql_processor.SqlConfig`, `abc.ABC`

**Subclasses:** `airbyte.caches.bigquery.BigQueryCache`

#### Attributes {#airbyte.caches.bigquery.BigQueryConfig--attributes}

- **`credentials_path`**&nbsp;(`str | None`)

  The path to the credentials file to use.
  If not passed, falls back to the default inferred from the environment.

- **`database_name`**&nbsp;(`str`)

  The name of the project to use. In BigQuery, this is equivalent to the database name.

- **`dataset_location`**&nbsp;(`str`)

  The geographic location of the BigQuery dataset (e.g., 'US', 'EU', etc.).
  Defaults to 'US'. See: https://cloud.google.com/bigquery/docs/locations

- **`dataset_name`**&nbsp;(`str`)

  Return the dataset name (alias of self.schema_name).

- **`project_name`**&nbsp;(`str`)

  Return the project name (alias of self.database_name).

#### `get_database_name` {#airbyte.caches.bigquery.BigQueryConfig.get_database_name}

<ApiMember kind="method">

<ApiSignature>

```python
def get_database_name(self) -> str
```

</ApiSignature>

Return the name of the database. For BigQuery, this is the project name.

</ApiMember>

#### `get_sql_alchemy_url` {#airbyte.caches.bigquery.BigQueryConfig.get_sql_alchemy_url}

<ApiMember kind="method">

<ApiSignature>

```python
def get_sql_alchemy_url(self) -> airbyte.secrets.base.SecretString
```

</ApiSignature>

Return the SQLAlchemy URL to use.

We suppress warnings about unrecognized JSON type. More info on that here:
- https://github.com/airbytehq/PyAirbyte/issues/254

</ApiMember>

#### `get_vendor_client` {#airbyte.caches.bigquery.BigQueryConfig.get_vendor_client}

<ApiMember kind="method">

<ApiSignature>

```python
def get_vendor_client(self) -> google.cloud.bigquery.client.Client
```

</ApiSignature>

Return a BigQuery python client.

</ApiMember>

</ApiMember>