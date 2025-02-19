## bigquery

raw table create logic is here https://github.com/airbytehq/airbyte/blob/ee1c21c2b19ed66bd6929e9ac95b2afcf09ce68a/airbyte-integrations/connectors/destination-bigquery/src/main/kotlin/io/airbyte/integrations/destination/bigquery/BigQueryUtils.kt#L93

queries to create all the relevant tables:
```sql
DROP SCHEMA IF EXISTS `dataline-integration-testing`.no_raw_tables_experiment CASCADE;
CREATE SCHEMA `dataline-integration-testing`.no_raw_tables_experiment OPTIONS (location="us-east1");

CREATE OR REPLACE TABLE `dataline-integration-testing`.no_raw_tables_experiment.input_typed_data_full (
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

LOAD DATA OVERWRITE `dataline-integration-testing`.no_raw_tables_experiment.input_typed_data_full (
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
  uris = ['gs://no_raw_tables/massive_data_2_final_version_(1)_final_10MB.csv'],
  skip_leading_rows = 1
);

CREATE OR REPLACE TABLE `dataline-integration-testing`.no_raw_tables_experiment.input_typed_data_part1
AS SELECT * FROM `dataline-integration-testing`.no_raw_tables_experiment.input_typed_data_full
  WHERE `string` >= 'Z';
CREATE OR REPLACE TABLE `dataline-integration-testing`.no_raw_tables_experiment.input_typed_data_part2
AS SELECT * FROM `dataline-integration-testing`.no_raw_tables_experiment.input_typed_data_full
  WHERE `string` <= 'a';

CREATE OR REPLACE TABLE `dataline-integration-testing`.no_raw_tables_experiment.old_raw_table_5mb_part1 (
  _airbyte_raw_id STRING,
  _airbyte_extracted_at TIMESTAMP,
  _airbyte_loaded_at TIMESTAMP,
  _airbyte_data STRING,
  _airbyte_meta STRING,
  _airbyte_generation_id INT64
)
PARTITION BY
  RANGE_BUCKET(_airbyte_generation_id, GENERATE_ARRAY(0, 10000, 5))
CLUSTER BY
  _airbyte_extracted_at
AS SELECT
  generate_uuid(),
  ts_with_tz,
  cast(null as timestamp),
  to_json_string(t),
  "{\"changes\":[],\"sync_id\":42}",
  42
FROM `dataline-integration-testing`.no_raw_tables_experiment.input_typed_data_part1 AS t;
CREATE OR REPLACE TABLE `dataline-integration-testing`.no_raw_tables_experiment.old_raw_table_5mb_part2 (
  _airbyte_raw_id STRING,
  _airbyte_extracted_at TIMESTAMP,
  _airbyte_loaded_at TIMESTAMP,
  _airbyte_data STRING,
  _airbyte_meta STRING,
  _airbyte_generation_id INT64
)
PARTITION BY
  RANGE_BUCKET(_airbyte_generation_id, GENERATE_ARRAY(0, 10000, 5))
CLUSTER BY
  _airbyte_extracted_at
AS SELECT
  generate_uuid(),
  ts_with_tz,
  cast(null as timestamp),
  to_json_string(t),
  "{\"changes\":[],\"sync_id\":42}",
  42
FROM `dataline-integration-testing`.no_raw_tables_experiment.input_typed_data_part2 AS t;

CREATE OR REPLACE TABLE `dataline-integration-testing`.no_raw_tables_experiment.new_input_table_5mb_part1 (
  _airbyte_raw_id STRING,
  _airbyte_extracted_at TIMESTAMP,
  _airbyte_meta JSON,
  _airbyte_generation_id INT64,
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
) AS SELECT
  generate_uuid(),
  ts_with_tz,
  JSON '{"changes":[],"sync_id":42}',
  42,
  *
FROM `dataline-integration-testing`.no_raw_tables_experiment.input_typed_data_part1 AS t;
CREATE OR REPLACE TABLE `dataline-integration-testing`.no_raw_tables_experiment.new_input_table_5mb_part2 (
  _airbyte_raw_id STRING,
  _airbyte_extracted_at TIMESTAMP,
  _airbyte_meta JSON,
  _airbyte_generation_id INT64,
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
) AS SELECT
  generate_uuid(),
  ts_with_tz,
  JSON '{"changes":[],"sync_id":42}',
  42,
  *
FROM `dataline-integration-testing`.no_raw_tables_experiment.input_typed_data_part2 AS t;
```

### pure deduping query

simulate a full refresh dedup, by upserting the entire dataset into itself.

```sql
MERGE `dataline-integration-testing`.`no_raw_tables_experiment`.`new_final_table_10mb` target_table
USING (
  WITH new_records AS (
    SELECT *
    FROM `dataline-integration-testing`.`no_raw_tables_experiment`.`new_table_10mb`
  ), numbered_rows AS (
    SELECT *, row_number() OVER (
      PARTITION BY `primary_key` ORDER BY `cursor` DESC NULLS LAST, `_airbyte_extracted_at` DESC
    ) AS row_number
    FROM new_records
  )
  SELECT
    `primary_key`,
    `cursor`,
    `string`,
    `bool`,
    `integer`,
    `float`,
    `date`,
    `ts_with_tz`,
    `ts_without_tz`,
    `time_with_tz`,
    `time_no_tz`,
    `array`,
    `json_object`,
    _airbyte_meta,
    _airbyte_raw_id,
    _airbyte_extracted_at,
    _airbyte_generation_id
  FROM numbered_rows
  WHERE row_number = 1
) new_record
ON (target_table.`primary_key` = new_record.`primary_key` OR (target_table.`primary_key` IS NULL AND new_record.`primary_key` IS NULL))
WHEN MATCHED AND (
  target_table.`cursor` < new_record.`cursor`
  OR (target_table.`cursor` = new_record.`cursor` AND target_table._airbyte_extracted_at < new_record._airbyte_extracted_at)
  OR (target_table.`cursor` IS NULL AND new_record.`cursor` IS NULL AND target_table._airbyte_extracted_at < new_record._airbyte_extracted_at)
  OR (target_table.`cursor` IS NULL AND new_record.`cursor` IS NOT NULL)
)
THEN UPDATE SET
  `primary_key` = new_record.`primary_key`,
  `cursor` = new_record.`cursor`,
  `string` = new_record.`string`,
  `bool` = new_record.`bool`,
  `integer` = new_record.`integer`,
  `float` = new_record.`float`,
  `date` = new_record.`date`,
  `ts_with_tz` = new_record.`ts_with_tz`,
  `ts_without_tz` = new_record.`ts_without_tz`,
  `time_with_tz` = new_record.`time_with_tz`,
  `time_no_tz` = new_record.`time_no_tz`,
  `array` = new_record.`array`,
  `json_object` = new_record.`json_object`,
  _airbyte_meta = new_record._airbyte_meta,
  _airbyte_raw_id = new_record._airbyte_raw_id,
  _airbyte_extracted_at = new_record._airbyte_extracted_at,
  _airbyte_generation_id = new_record._airbyte_generation_id
WHEN NOT MATCHED THEN INSERT (
  `primary_key`,
  `cursor`,
  `string`,
  `bool`,
  `integer`,
  `float`,
  `date`,
  `ts_with_tz`,
  `ts_without_tz`,
  `time_with_tz`,
  `time_no_tz`,
  `array`,
  `json_object`,
  _airbyte_meta,
  _airbyte_raw_id,
  _airbyte_extracted_at,
  _airbyte_generation_id
) VALUES (
  new_record.`primary_key`,
  new_record.`cursor`,
  new_record.`string`,
  new_record.`bool`,
  new_record.`integer`,
  new_record.`float`,
  new_record.`date`,
  new_record.`ts_with_tz`,
  new_record.`ts_without_tz`,
  new_record.`time_with_tz`,
  new_record.`time_no_tz`,
  new_record.`array`,
  new_record.`json_object`,
  new_record._airbyte_meta,
  new_record._airbyte_raw_id,
  new_record._airbyte_extracted_at,
  new_record._airbyte_generation_id
);
```
