-- naive create table --------------------------------
DROP TABLE `dataline-integration-testing`.`no_raw_tables_experiment`.`new_final_table_5mb`;
CREATE OR REPLACE TABLE `dataline-integration-testing`.`no_raw_tables_experiment`.`new_final_table_5mb` (
  _airbyte_raw_id STRING NOT NULL,
  _airbyte_extracted_at TIMESTAMP NOT NULL,
  _airbyte_meta JSON NOT NULL,
  _airbyte_generation_id INTEGER,
  
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
PARTITION BY (DATE_TRUNC(_airbyte_extracted_at, DAY))
CLUSTER BY `primary_key`, `_airbyte_extracted_at`;










-- "naive" dedup query -------------------------------
MERGE `dataline-integration-testing`.`no_raw_tables_experiment`.`new_final_table_5mb` target_table
USING (
  WITH new_records AS (
    SELECT *
    FROM `dataline-integration-testing`.`no_raw_tables_experiment`.`new_input_table_5mb_part1`
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










-- optimized create table --------------------------------
DROP TABLE `dataline-integration-testing`.`no_raw_tables_experiment`.`new_final_table_5mb`;
CREATE OR REPLACE TABLE `dataline-integration-testing`.`no_raw_tables_experiment`.`new_final_table_5mb` (
  _airbyte_raw_id STRING NOT NULL,
  _airbyte_extracted_at TIMESTAMP NOT NULL,
  _airbyte_meta JSON NOT NULL,
  _airbyte_generation_id INTEGER,
  _airbyte_partition_key INTEGER,
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
PARTITION BY (RANGE_BUCKET(_airbyte_partition_key, GENERATE_ARRAY(0, 10000, 10)))
CLUSTER BY `primary_key`, `_airbyte_extracted_at`;










-- "optimized" dedup query -------------------------------
MERGE `dataline-integration-testing`.`no_raw_tables_experiment`.`new_final_table_5mb` target_table
USING (
  WITH new_records AS (
    SELECT *
    FROM `dataline-integration-testing`.`no_raw_tables_experiment`.`new_input_table_5mb_part1`
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
    , mod(`primary_key`, 10000) as _airbyte_partition_key
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
  , _airbyte_partition_key = new_record._airbyte_partition_key
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
  , _airbyte_partition_key
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
  , new_record._airbyte_partition_key
);
