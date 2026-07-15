---
id: airbyte-caches-bigquery
title: airbyte.caches.bigquery
---

Module airbyte.caches.bigquery
==============================
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

Classes
-------

`BigQueryCache(**data: Any)`
:   The BigQuery cache implementation.
    
    Initialize the cache and backends.

    ### Ancestors (in MRO)

    * airbyte._processors.sql.bigquery.BigQueryConfig
    * airbyte.caches.base.CacheBase
    * airbyte.shared.sql_processor.SqlConfig
    * pydantic.main.BaseModel
    * airbyte._writers.base.AirbyteWriterInterface
    * abc.ABC

    ### Class variables

    `model_config`
    :

    `paired_destination_config_class: ClassVar[type | None]`
    :   DestinationBigquery(dataset_id: 'str', dataset_location: 'DatasetLocation', project_id: 'str', cdc_deletion_mode: 'Optional[CDCDeletionMode]' = &lt;CDCDeletionMode.HARD_DELETE: 'Hard delete'&gt;, credentials_json: 'Optional[str]' = None, DESTINATION_TYPE: 'Final[Bigquery]' = &lt;Bigquery.BIGQUERY: 'bigquery'&gt;, disable_type_dedupe: 'Optional[bool]' = False, loading_method: 'Optional[LoadingMethod]' = None, raw_data_dataset: 'Optional[str]' = None)

    `paired_destination_name: ClassVar[str | None]`
    :

    ### Methods

    `get_arrow_dataset(self, stream_name: str, *, max_chunk_size: int = 100000) ‑> NoReturn`
    :   Raises NotImplementedError; BigQuery doesn't support `pd.read_sql_table`.
        
        See: https://github.com/airbytehq/PyAirbyte/issues/165

`BigQueryConfig(**data: Any)`
:   Configuration for BigQuery.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte.shared.sql_processor.SqlConfig
    * pydantic.main.BaseModel
    * abc.ABC

    ### Descendants

    * airbyte.caches.bigquery.BigQueryCache

    ### Class variables

    `credentials_path: str | None`
    :   The path to the credentials file to use.
        If not passed, falls back to the default inferred from the environment.

    `database_name: str`
    :   The name of the project to use. In BigQuery, this is equivalent to the database name.

    `dataset_location: str`
    :   The geographic location of the BigQuery dataset (e.g., 'US', 'EU', etc.).
        Defaults to 'US'. See: https://cloud.google.com/bigquery/docs/locations

    `model_config`
    :

    ### Instance variables

    `dataset_name: str`
    :   Return the dataset name (alias of self.schema_name).

    `project_name: str`
    :   Return the project name (alias of self.database_name).

    ### Methods

    `get_database_name(self) ‑> str`
    :   Return the name of the database. For BigQuery, this is the project name.

    `get_sql_alchemy_url(self) ‑> airbyte.secrets.base.SecretString`
    :   Return the SQLAlchemy URL to use.
        
        We suppress warnings about unrecognized JSON type. More info on that here:
        - https://github.com/airbytehq/PyAirbyte/issues/254

    `get_vendor_client(self) ‑> google.cloud.bigquery.client.Client`
    :   Return a BigQuery python client.