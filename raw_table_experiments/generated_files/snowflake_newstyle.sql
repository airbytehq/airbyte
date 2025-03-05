-- naive create table --------------------------------
DROP TABLE IF EXISTS PUBLIC."new_final_table_50gb";
create table PUBLIC."new_final_table_50gb" (
  "_AIRBYTE_RAW_ID" TEXT NOT NULL COLLATE 'utf8',
  "_AIRBYTE_EXTRACTED_AT" TIMESTAMP_TZ NOT NULL,
  "_AIRBYTE_META" VARIANT NOT NULL,
  "_AIRBYTE_GENERATION_ID" INTEGER
  , "primary_key" NUMBER
  , "cursor" TIMESTAMP_NTZ
  , "string" TEXT
  , "bool" BOOLEAN
  , "integer" NUMBER
  , "float" FLOAT
  , "date" DATE
  , "ts_with_tz" TIMESTAMP_TZ
  , "ts_no_tz" TIMESTAMP_NTZ
  , "time_with_tz" TEXT
  , "time_no_tz" TIME
  , "array" ARRAY
  , "json_object" OBJECT
  ) data_retention_time_in_days = 2;










-- "naive" dedup query -------------------------------
INSERT INTO PUBLIC."new_final_table_50gb"(
    "primary_key",
    "cursor",
    "string",
    "bool",
    "integer",
    "float",
    "date",
    "ts_with_tz",
    "ts_no_tz",
    "time_with_tz",
    "time_no_tz",
    "array",
    "json_object",
    _AIRBYTE_RAW_ID,
    _AIRBYTE_EXTRACTED_AT,
    _AIRBYTE_GENERATION_ID,
    "_AIRBYTE_META"
)
WITH new_records AS (
  SELECT
    "primary_key", 
    "cursor", 
    "string", 
    "bool", 
    "integer", 
    "float", 
    "date", 
    "ts_with_tz", 
    "ts_no_tz", 
    "time_with_tz", 
    "time_no_tz", 
    "array", 
    "json_object", 
    "_AIRBYTE_RAW_ID",
    "_AIRBYTE_EXTRACTED_AT", 
    "_AIRBYTE_GENERATION_ID", 
    "_AIRBYTE_META",
    row_number() OVER (
      PARTITION BY "primary_key" ORDER BY "cursor" DESC NULLS LAST, "_AIRBYTE_EXTRACTED_AT" DESC
    ) AS row_number
  FROM PUBLIC."new_input_table_50gb_part1"
)
SELECT
    "primary_key",
    "cursor",
    "string",
    "bool",
    "integer",
    "float",
    "date",
    "ts_with_tz",
    "ts_no_tz",
    "time_with_tz",
    "time_no_tz",
    "array",
    "json_object",
    _AIRBYTE_RAW_ID,
    _AIRBYTE_EXTRACTED_AT,
    _AIRBYTE_GENERATION_ID,
    "_AIRBYTE_META"
FROM
    new_records
WHERE row_number = 1;
DELETE FROM 
  "PUBLIC"."new_final_table_50gb"
WHERE 
  "_AIRBYTE_RAW_ID" IN (
    SELECT "_AIRBYTE_RAW_ID" FROM (
      SELECT 
        "_AIRBYTE_RAW_ID", 
        row_number() OVER (PARTITION BY "primary_key" ORDER BY "cursor" DESC NULLS LAST, TIMESTAMPADD(
  HOUR, 
  EXTRACT(timezone_hour from "_AIRBYTE_EXTRACTED_AT"), 
  TIMESTAMPADD(
    MINUTE,
    EXTRACT(timezone_minute from "_AIRBYTE_EXTRACTED_AT"),
    CONVERT_TIMEZONE('UTC', "_AIRBYTE_EXTRACTED_AT")
  )
) DESC) 
        as row_number 
      FROM 
        "PUBLIC"."new_final_table_50gb"
    )
    WHERE row_number != 1
  );
