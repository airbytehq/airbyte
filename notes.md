## bigquery

raw table create logic is here https://github.com/airbytehq/airbyte/blob/ee1c21c2b19ed66bd6929e9ac95b2afcf09ce68a/airbyte-integrations/connectors/destination-bigquery/src/main/kotlin/io/airbyte/integrations/destination/bigquery/BigQueryUtils.kt#L93

equivalent sql:
```sql
CREATE TABLE dataline-integration-testing.no_raw_tables_experiment.<raw_table_name> (
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

also ran this query to create+load the typed table:
```sql
CREATE TABLE dataline-integration-testing.no_raw_tables_experiment.input_typed_data (
  `primary_key` INT64,
  `cursor` DATETIME,
  `string` STRING,
  `bool` BOOL,
  `integer` INT64,
  `float` NUMERIC,
  `date` DATE,
  `ts_with_tz` TIMESTAMP,
  `ts_without_tz` DATETIME,
  `time_with_tz` STRING,
  `time_no_tz` TIME,
  `array` JSON,
  `json_object` JSON
);

LOAD DATA OVERWRITE dataline-integration-testing.no_raw_tables_experiment.input_typed_data (
  `primary_key` INT64,
  `cursor` DATETIME,
  `string` STRING,
  `bool` BOOL,
  `integer` INT64,
  `float` NUMERIC,
  `date` DATE,
  `ts_with_tz` TIMESTAMP,
  `ts_without_tz` DATETIME,
  `time_with_tz` STRING,
  `time_no_tz` TIME,
  `array` JSON,
  `json_object` JSON
)
FROM FILES (
  format = 'CSV',
  uris = ['gs://no_raw_tables/massive_data_10MB.csv'],
  skip_leading_rows = 1
);
```
