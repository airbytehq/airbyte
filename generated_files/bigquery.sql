-- create table --------------------------------
CREATE  TABLE `dataline-integration-testing`.`no_raw_tables_experiment`.`typing_deduping_final_table` (
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
`timestamp_with_timezone` TIMESTAMP,
`timestamp_without_timezone` DATETIME,
`time_with_timezone` STRING,
`time_without_timezone` TIME,
`array` JSON,
`json_object` JSON
)
PARTITION BY (DATE_TRUNC(_airbyte_extracted_at, DAY))
CLUSTER BY `primary_key`, `_airbyte_extracted_at`;











-- "fast" T+D query -------------------------------
MERGE `dataline-integration-testing`.`no_raw_tables_experiment`.`typing_deduping_final_table` target_table
USING (
  WITH intermediate_data AS (
  SELECT
CAST(JSON_VALUE(`_airbyte_data`, '$."primary_key"') as INT64) as `primary_key`,
CAST(JSON_VALUE(`_airbyte_data`, '$."cursor"') as DATETIME) as `cursor`,
(CASE
      WHEN JSON_QUERY(`_airbyte_data`, '$."string"') IS NULL
        OR JSON_TYPE(PARSE_JSON(JSON_QUERY(`_airbyte_data`, '$."string"'), wide_number_mode=>'round')) != 'string'
        THEN JSON_QUERY(`_airbyte_data`, '$."string"')
    ELSE
    JSON_VALUE(`_airbyte_data`, '$."string"')
  END)
 as `string`,
CAST(JSON_VALUE(`_airbyte_data`, '$."bool"') as BOOL) as `bool`,
CAST(JSON_VALUE(`_airbyte_data`, '$."integer"') as INT64) as `integer`,
CAST(JSON_VALUE(`_airbyte_data`, '$."float"') as NUMERIC) as `float`,
CAST(JSON_VALUE(`_airbyte_data`, '$."date"') as DATE) as `date`,
CAST(JSON_VALUE(`_airbyte_data`, '$."timestamp_with_timezone"') as TIMESTAMP) as `timestamp_with_timezone`,
CAST(JSON_VALUE(`_airbyte_data`, '$."timestamp_without_timezone"') as DATETIME) as `timestamp_without_timezone`,
JSON_VALUE(`_airbyte_data`, '$."time_with_timezone"') as `time_with_timezone`,
CAST(JSON_VALUE(`_airbyte_data`, '$."time_without_timezone"') as TIME) as `time_without_timezone`,
PARSE_JSON(CASE
  WHEN JSON_QUERY(`_airbyte_data`, '$."array"') IS NULL
    OR JSON_TYPE(PARSE_JSON(JSON_QUERY(`_airbyte_data`, '$."array"'), wide_number_mode=>'round')) != 'array'
    THEN NULL
  ELSE JSON_QUERY(`_airbyte_data`, '$."array"')
END, wide_number_mode=>'round')
 as `array`,
PARSE_JSON(CASE
  WHEN JSON_QUERY(`_airbyte_data`, '$."json_object"') IS NULL
    OR JSON_TYPE(PARSE_JSON(JSON_QUERY(`_airbyte_data`, '$."json_object"'), wide_number_mode=>'round')) != 'object'
    THEN NULL
  ELSE JSON_QUERY(`_airbyte_data`, '$."json_object"')
END, wide_number_mode=>'round')
 as `json_object`,
  [] AS column_errors,
  _airbyte_raw_id,
  _airbyte_extracted_at,
  _airbyte_meta,
  _airbyte_generation_id
  FROM `dataline-integration-testing`.`no_raw_tables_experiment`.`input_raw_table`
  WHERE (
      _airbyte_loaded_at IS NULL
      
    ) 
), new_records AS (
  SELECT
  `primary_key`,
`cursor`,
`string`,
`bool`,
`integer`,
`float`,
`date`,
`timestamp_with_timezone`,
`timestamp_without_timezone`,
`time_with_timezone`,
`time_without_timezone`,
`array`,
`json_object`,
    to_json(json_set(
      coalesce(parse_json(_airbyte_meta), JSON'{}'),
      '$.changes',
      json_array_append(
        coalesce(json_query(parse_json(_airbyte_meta), '$.changes'), JSON'[]'),
        '$',
        COALESCE((SELECT ARRAY_AGG(unnested_column_errors IGNORE NULLS) FROM UNNEST(column_errors) unnested_column_errors), [])
       )
    )) as _airbyte_meta,
    _airbyte_raw_id,
    _airbyte_extracted_at,
    _airbyte_generation_id
  FROM intermediate_data
), numbered_rows AS (
  SELECT *, row_number() OVER (
    PARTITION BY `primary_key` ORDER BY `cursor` DESC NULLS LAST, `_airbyte_extracted_at` DESC
  ) AS row_number
  FROM new_records
)
SELECT `primary_key`,
`cursor`,
`string`,
`bool`,
`integer`,
`float`,
`date`,
`timestamp_with_timezone`,
`timestamp_without_timezone`,
`time_with_timezone`,
`time_without_timezone`,
`array`,
`json_object`, _airbyte_meta, _airbyte_raw_id, _airbyte_extracted_at, _airbyte_generation_id
FROM numbered_rows
WHERE row_number = 1
) new_record
ON (target_table.`primary_key` = new_record.`primary_key` OR (target_table.`primary_key` IS NULL AND new_record.`primary_key` IS NULL))

WHEN MATCHED AND (target_table.`cursor` < new_record.`cursor` OR (target_table.`cursor` = new_record.`cursor` AND target_table._airbyte_extracted_at < new_record._airbyte_extracted_at) OR (target_table.`cursor` IS NULL AND new_record.`cursor` IS NULL AND target_table._airbyte_extracted_at < new_record._airbyte_extracted_at) OR (target_table.`cursor` IS NULL AND new_record.`cursor` IS NOT NULL)) THEN UPDATE SET
  `primary_key` = new_record.`primary_key`,
`cursor` = new_record.`cursor`,
`string` = new_record.`string`,
`bool` = new_record.`bool`,
`integer` = new_record.`integer`,
`float` = new_record.`float`,
`date` = new_record.`date`,
`timestamp_with_timezone` = new_record.`timestamp_with_timezone`,
`timestamp_without_timezone` = new_record.`timestamp_without_timezone`,
`time_with_timezone` = new_record.`time_with_timezone`,
`time_without_timezone` = new_record.`time_without_timezone`,
`array` = new_record.`array`,
`json_object` = new_record.`json_object`,
  _airbyte_meta = new_record._airbyte_meta,
  _airbyte_raw_id = new_record._airbyte_raw_id,
  _airbyte_extracted_at = new_record._airbyte_extracted_at,
  _airbyte_generation_id = new_record._airbyte_generation_id
WHEN NOT MATCHED  THEN INSERT (
  `primary_key`,
`cursor`,
`string`,
`bool`,
`integer`,
`float`,
`date`,
`timestamp_with_timezone`,
`timestamp_without_timezone`,
`time_with_timezone`,
`time_without_timezone`,
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
new_record.`timestamp_with_timezone`,
new_record.`timestamp_without_timezone`,
new_record.`time_with_timezone`,
new_record.`time_without_timezone`,
new_record.`array`,
new_record.`json_object`,
  new_record._airbyte_meta,
  new_record._airbyte_raw_id,
  new_record._airbyte_extracted_at,
  new_record._airbyte_generation_id
);
UPDATE `dataline-integration-testing`.`no_raw_tables_experiment`.`input_raw_table`
SET `_airbyte_loaded_at` = CURRENT_TIMESTAMP()
WHERE `_airbyte_loaded_at` IS NULL
  
;










-- "slow" T+D query -------------------------------
MERGE `dataline-integration-testing`.`no_raw_tables_experiment`.`typing_deduping_final_table` target_table
USING (
  WITH intermediate_data AS (
  SELECT
SAFE_CAST(JSON_VALUE(`_airbyte_data`, '$."primary_key"') as INT64) as `primary_key`,
SAFE_CAST(JSON_VALUE(`_airbyte_data`, '$."cursor"') as DATETIME) as `cursor`,
(CASE
      WHEN JSON_QUERY(`_airbyte_data`, '$."string"') IS NULL
        OR JSON_TYPE(PARSE_JSON(JSON_QUERY(`_airbyte_data`, '$."string"'), wide_number_mode=>'round')) != 'string'
        THEN JSON_QUERY(`_airbyte_data`, '$."string"')
    ELSE
    JSON_VALUE(`_airbyte_data`, '$."string"')
  END)
 as `string`,
SAFE_CAST(JSON_VALUE(`_airbyte_data`, '$."bool"') as BOOL) as `bool`,
SAFE_CAST(JSON_VALUE(`_airbyte_data`, '$."integer"') as INT64) as `integer`,
SAFE_CAST(JSON_VALUE(`_airbyte_data`, '$."float"') as NUMERIC) as `float`,
SAFE_CAST(JSON_VALUE(`_airbyte_data`, '$."date"') as DATE) as `date`,
SAFE_CAST(JSON_VALUE(`_airbyte_data`, '$."timestamp_with_timezone"') as TIMESTAMP) as `timestamp_with_timezone`,
SAFE_CAST(JSON_VALUE(`_airbyte_data`, '$."timestamp_without_timezone"') as DATETIME) as `timestamp_without_timezone`,
JSON_VALUE(`_airbyte_data`, '$."time_with_timezone"') as `time_with_timezone`,
SAFE_CAST(JSON_VALUE(`_airbyte_data`, '$."time_without_timezone"') as TIME) as `time_without_timezone`,
PARSE_JSON(CASE
  WHEN JSON_QUERY(`_airbyte_data`, '$."array"') IS NULL
    OR JSON_TYPE(PARSE_JSON(JSON_QUERY(`_airbyte_data`, '$."array"'), wide_number_mode=>'round')) != 'array'
    THEN NULL
  ELSE JSON_QUERY(`_airbyte_data`, '$."array"')
END, wide_number_mode=>'round')
 as `array`,
PARSE_JSON(CASE
  WHEN JSON_QUERY(`_airbyte_data`, '$."json_object"') IS NULL
    OR JSON_TYPE(PARSE_JSON(JSON_QUERY(`_airbyte_data`, '$."json_object"'), wide_number_mode=>'round')) != 'object'
    THEN NULL
  ELSE JSON_QUERY(`_airbyte_data`, '$."json_object"')
END, wide_number_mode=>'round')
 as `json_object`,
  [CASE
  WHEN (JSON_QUERY(PARSE_JSON(`_airbyte_data`, wide_number_mode=>'round'), '$."primary_key"') IS NOT NULL)
    AND (JSON_TYPE(JSON_QUERY(PARSE_JSON(`_airbyte_data`, wide_number_mode=>'round'), '$."primary_key"')) != 'null')
    AND (SAFE_CAST(JSON_VALUE(`_airbyte_data`, '$."primary_key"') as INT64) IS NULL)
    THEN JSON '{"field":"primary_key","change":"NULLED","reason":"DESTINATION_TYPECAST_ERROR"}'
  ELSE NULL
END,
CASE
  WHEN (JSON_QUERY(PARSE_JSON(`_airbyte_data`, wide_number_mode=>'round'), '$."cursor"') IS NOT NULL)
    AND (JSON_TYPE(JSON_QUERY(PARSE_JSON(`_airbyte_data`, wide_number_mode=>'round'), '$."cursor"')) != 'null')
    AND (SAFE_CAST(JSON_VALUE(`_airbyte_data`, '$."cursor"') as DATETIME) IS NULL)
    THEN JSON '{"field":"cursor","change":"NULLED","reason":"DESTINATION_TYPECAST_ERROR"}'
  ELSE NULL
END,
CASE
  WHEN (JSON_QUERY(PARSE_JSON(`_airbyte_data`, wide_number_mode=>'round'), '$."string"') IS NOT NULL)
    AND (JSON_TYPE(JSON_QUERY(PARSE_JSON(`_airbyte_data`, wide_number_mode=>'round'), '$."string"')) != 'null')
    AND ((CASE
      WHEN JSON_QUERY(`_airbyte_data`, '$."string"') IS NULL
        OR JSON_TYPE(PARSE_JSON(JSON_QUERY(`_airbyte_data`, '$."string"'), wide_number_mode=>'round')) != 'string'
        THEN JSON_QUERY(`_airbyte_data`, '$."string"')
    ELSE
    JSON_VALUE(`_airbyte_data`, '$."string"')
  END)
 IS NULL)
    THEN JSON '{"field":"string","change":"NULLED","reason":"DESTINATION_TYPECAST_ERROR"}'
  ELSE NULL
END,
CASE
  WHEN (JSON_QUERY(PARSE_JSON(`_airbyte_data`, wide_number_mode=>'round'), '$."bool"') IS NOT NULL)
    AND (JSON_TYPE(JSON_QUERY(PARSE_JSON(`_airbyte_data`, wide_number_mode=>'round'), '$."bool"')) != 'null')
    AND (SAFE_CAST(JSON_VALUE(`_airbyte_data`, '$."bool"') as BOOL) IS NULL)
    THEN JSON '{"field":"bool","change":"NULLED","reason":"DESTINATION_TYPECAST_ERROR"}'
  ELSE NULL
END,
CASE
  WHEN (JSON_QUERY(PARSE_JSON(`_airbyte_data`, wide_number_mode=>'round'), '$."integer"') IS NOT NULL)
    AND (JSON_TYPE(JSON_QUERY(PARSE_JSON(`_airbyte_data`, wide_number_mode=>'round'), '$."integer"')) != 'null')
    AND (SAFE_CAST(JSON_VALUE(`_airbyte_data`, '$."integer"') as INT64) IS NULL)
    THEN JSON '{"field":"integer","change":"NULLED","reason":"DESTINATION_TYPECAST_ERROR"}'
  ELSE NULL
END,
CASE
  WHEN (JSON_QUERY(PARSE_JSON(`_airbyte_data`, wide_number_mode=>'round'), '$."float"') IS NOT NULL)
    AND (JSON_TYPE(JSON_QUERY(PARSE_JSON(`_airbyte_data`, wide_number_mode=>'round'), '$."float"')) != 'null')
    AND (SAFE_CAST(JSON_VALUE(`_airbyte_data`, '$."float"') as NUMERIC) IS NULL)
    THEN JSON '{"field":"float","change":"NULLED","reason":"DESTINATION_TYPECAST_ERROR"}'
  ELSE NULL
END,
CASE
  WHEN (JSON_QUERY(PARSE_JSON(`_airbyte_data`, wide_number_mode=>'round'), '$."date"') IS NOT NULL)
    AND (JSON_TYPE(JSON_QUERY(PARSE_JSON(`_airbyte_data`, wide_number_mode=>'round'), '$."date"')) != 'null')
    AND (SAFE_CAST(JSON_VALUE(`_airbyte_data`, '$."date"') as DATE) IS NULL)
    THEN JSON '{"field":"date","change":"NULLED","reason":"DESTINATION_TYPECAST_ERROR"}'
  ELSE NULL
END,
CASE
  WHEN (JSON_QUERY(PARSE_JSON(`_airbyte_data`, wide_number_mode=>'round'), '$."timestamp_with_timezone"') IS NOT NULL)
    AND (JSON_TYPE(JSON_QUERY(PARSE_JSON(`_airbyte_data`, wide_number_mode=>'round'), '$."timestamp_with_timezone"')) != 'null')
    AND (SAFE_CAST(JSON_VALUE(`_airbyte_data`, '$."timestamp_with_timezone"') as TIMESTAMP) IS NULL)
    THEN JSON '{"field":"timestamp_with_timezone","change":"NULLED","reason":"DESTINATION_TYPECAST_ERROR"}'
  ELSE NULL
END,
CASE
  WHEN (JSON_QUERY(PARSE_JSON(`_airbyte_data`, wide_number_mode=>'round'), '$."timestamp_without_timezone"') IS NOT NULL)
    AND (JSON_TYPE(JSON_QUERY(PARSE_JSON(`_airbyte_data`, wide_number_mode=>'round'), '$."timestamp_without_timezone"')) != 'null')
    AND (SAFE_CAST(JSON_VALUE(`_airbyte_data`, '$."timestamp_without_timezone"') as DATETIME) IS NULL)
    THEN JSON '{"field":"timestamp_without_timezone","change":"NULLED","reason":"DESTINATION_TYPECAST_ERROR"}'
  ELSE NULL
END,
CASE
  WHEN (JSON_QUERY(PARSE_JSON(`_airbyte_data`, wide_number_mode=>'round'), '$."time_with_timezone"') IS NOT NULL)
    AND (JSON_TYPE(JSON_QUERY(PARSE_JSON(`_airbyte_data`, wide_number_mode=>'round'), '$."time_with_timezone"')) != 'null')
    AND (JSON_VALUE(`_airbyte_data`, '$."time_with_timezone"') IS NULL)
    THEN JSON '{"field":"time_with_timezone","change":"NULLED","reason":"DESTINATION_TYPECAST_ERROR"}'
  ELSE NULL
END,
CASE
  WHEN (JSON_QUERY(PARSE_JSON(`_airbyte_data`, wide_number_mode=>'round'), '$."time_without_timezone"') IS NOT NULL)
    AND (JSON_TYPE(JSON_QUERY(PARSE_JSON(`_airbyte_data`, wide_number_mode=>'round'), '$."time_without_timezone"')) != 'null')
    AND (SAFE_CAST(JSON_VALUE(`_airbyte_data`, '$."time_without_timezone"') as TIME) IS NULL)
    THEN JSON '{"field":"time_without_timezone","change":"NULLED","reason":"DESTINATION_TYPECAST_ERROR"}'
  ELSE NULL
END,
CASE
  WHEN (JSON_QUERY(PARSE_JSON(`_airbyte_data`, wide_number_mode=>'round'), '$."array"') IS NOT NULL)
    AND (JSON_TYPE(JSON_QUERY(PARSE_JSON(`_airbyte_data`, wide_number_mode=>'round'), '$."array"')) != 'null')
    AND (PARSE_JSON(CASE
  WHEN JSON_QUERY(`_airbyte_data`, '$."array"') IS NULL
    OR JSON_TYPE(PARSE_JSON(JSON_QUERY(`_airbyte_data`, '$."array"'), wide_number_mode=>'round')) != 'array'
    THEN NULL
  ELSE JSON_QUERY(`_airbyte_data`, '$."array"')
END, wide_number_mode=>'round')
 IS NULL)
    THEN JSON '{"field":"array","change":"NULLED","reason":"DESTINATION_TYPECAST_ERROR"}'
  ELSE NULL
END,
CASE
  WHEN (JSON_QUERY(PARSE_JSON(`_airbyte_data`, wide_number_mode=>'round'), '$."json_object"') IS NOT NULL)
    AND (JSON_TYPE(JSON_QUERY(PARSE_JSON(`_airbyte_data`, wide_number_mode=>'round'), '$."json_object"')) != 'null')
    AND (PARSE_JSON(CASE
  WHEN JSON_QUERY(`_airbyte_data`, '$."json_object"') IS NULL
    OR JSON_TYPE(PARSE_JSON(JSON_QUERY(`_airbyte_data`, '$."json_object"'), wide_number_mode=>'round')) != 'object'
    THEN NULL
  ELSE JSON_QUERY(`_airbyte_data`, '$."json_object"')
END, wide_number_mode=>'round')
 IS NULL)
    THEN JSON '{"field":"json_object","change":"NULLED","reason":"DESTINATION_TYPECAST_ERROR"}'
  ELSE NULL
END] AS column_errors,
  _airbyte_raw_id,
  _airbyte_extracted_at,
  _airbyte_meta,
  _airbyte_generation_id
  FROM `dataline-integration-testing`.`no_raw_tables_experiment`.`input_raw_table`
  WHERE (
      _airbyte_loaded_at IS NULL
      
    ) 
), new_records AS (
  SELECT
  `primary_key`,
`cursor`,
`string`,
`bool`,
`integer`,
`float`,
`date`,
`timestamp_with_timezone`,
`timestamp_without_timezone`,
`time_with_timezone`,
`time_without_timezone`,
`array`,
`json_object`,
    to_json(json_set(
      coalesce(parse_json(_airbyte_meta), JSON'{}'),
      '$.changes',
      json_array_append(
        coalesce(json_query(parse_json(_airbyte_meta), '$.changes'), JSON'[]'),
        '$',
        COALESCE((SELECT ARRAY_AGG(unnested_column_errors IGNORE NULLS) FROM UNNEST(column_errors) unnested_column_errors), [])
       )
    )) as _airbyte_meta,
    _airbyte_raw_id,
    _airbyte_extracted_at,
    _airbyte_generation_id
  FROM intermediate_data
), numbered_rows AS (
  SELECT *, row_number() OVER (
    PARTITION BY `primary_key` ORDER BY `cursor` DESC NULLS LAST, `_airbyte_extracted_at` DESC
  ) AS row_number
  FROM new_records
)
SELECT `primary_key`,
`cursor`,
`string`,
`bool`,
`integer`,
`float`,
`date`,
`timestamp_with_timezone`,
`timestamp_without_timezone`,
`time_with_timezone`,
`time_without_timezone`,
`array`,
`json_object`, _airbyte_meta, _airbyte_raw_id, _airbyte_extracted_at, _airbyte_generation_id
FROM numbered_rows
WHERE row_number = 1
) new_record
ON (target_table.`primary_key` = new_record.`primary_key` OR (target_table.`primary_key` IS NULL AND new_record.`primary_key` IS NULL))

WHEN MATCHED AND (target_table.`cursor` < new_record.`cursor` OR (target_table.`cursor` = new_record.`cursor` AND target_table._airbyte_extracted_at < new_record._airbyte_extracted_at) OR (target_table.`cursor` IS NULL AND new_record.`cursor` IS NULL AND target_table._airbyte_extracted_at < new_record._airbyte_extracted_at) OR (target_table.`cursor` IS NULL AND new_record.`cursor` IS NOT NULL)) THEN UPDATE SET
  `primary_key` = new_record.`primary_key`,
`cursor` = new_record.`cursor`,
`string` = new_record.`string`,
`bool` = new_record.`bool`,
`integer` = new_record.`integer`,
`float` = new_record.`float`,
`date` = new_record.`date`,
`timestamp_with_timezone` = new_record.`timestamp_with_timezone`,
`timestamp_without_timezone` = new_record.`timestamp_without_timezone`,
`time_with_timezone` = new_record.`time_with_timezone`,
`time_without_timezone` = new_record.`time_without_timezone`,
`array` = new_record.`array`,
`json_object` = new_record.`json_object`,
  _airbyte_meta = new_record._airbyte_meta,
  _airbyte_raw_id = new_record._airbyte_raw_id,
  _airbyte_extracted_at = new_record._airbyte_extracted_at,
  _airbyte_generation_id = new_record._airbyte_generation_id
WHEN NOT MATCHED  THEN INSERT (
  `primary_key`,
`cursor`,
`string`,
`bool`,
`integer`,
`float`,
`date`,
`timestamp_with_timezone`,
`timestamp_without_timezone`,
`time_with_timezone`,
`time_without_timezone`,
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
new_record.`timestamp_with_timezone`,
new_record.`timestamp_without_timezone`,
new_record.`time_with_timezone`,
new_record.`time_without_timezone`,
new_record.`array`,
new_record.`json_object`,
  new_record._airbyte_meta,
  new_record._airbyte_raw_id,
  new_record._airbyte_extracted_at,
  new_record._airbyte_generation_id
);
UPDATE `dataline-integration-testing`.`no_raw_tables_experiment`.`input_raw_table`
SET `_airbyte_loaded_at` = CURRENT_TIMESTAMP()
WHERE `_airbyte_loaded_at` IS NULL
  
;
