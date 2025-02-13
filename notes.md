## bigquery

raw table create logic is here https://github.com/airbytehq/airbyte/blob/ee1c21c2b19ed66bd6929e9ac95b2afcf09ce68a/airbyte-integrations/connectors/destination-bigquery/src/main/kotlin/io/airbyte/integrations/destination/bigquery/BigQueryUtils.kt#L93

equivalent sql:
```sql
CREATE TABLE project.dataset.name (
  _airbyte_raw_id STRING,
  _airbyte_extracted_at TIMESTAMP,
  _airbyte_loaded_at TIMESTAMP,
  _airbyte_data STRING,
  _airbyte_meta STRING,
  _airbyte_generation_id INT64
)
PARTITION BY
  RANGE_BUCKET(_airbyte_generation_id, GENERATE_ARRAY(0, 10_000, 5))
CLUSTER BY
  _airbyte_extracted_at
```
