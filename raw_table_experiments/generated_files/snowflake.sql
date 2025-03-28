-- create table --------------------------------
CREATE  TABLE "PUBLIC"."old_final_table_5mb" (
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
, "ts_without_tz" TIMESTAMP_NTZ
, "time_with_tz" TEXT
, "time_no_tz" TIME
, "array" ARRAY
, "json_object" OBJECT
) data_retention_time_in_days = 2;










-- "fast" T+D query -------------------------------
INSERT INTO "PUBLIC"."old_final_table_5mb"(
  "primary_key", 
  "cursor", 
  "string", 
  "bool", 
  "integer", 
  "float", 
  "date", 
  "ts_with_tz", 
  "ts_without_tz", 
  "time_with_tz", 
  "time_no_tz", 
  "array", 
  "json_object", 
  _airbyte_raw_id, 
  _airbyte_extracted_at, 
  _airbyte_generation_id,
  "_AIRBYTE_META"
)
WITH intermediate_data AS (
  SELECT
    CAST(("_airbyte_data":"primary_key")::text as NUMBER) as "primary_key", 
    CAST(("_airbyte_data":"cursor")::text as TIMESTAMP_NTZ) as "cursor", 
    (("_airbyte_data":"string")::text) as "string", 
    CAST(("_airbyte_data":"bool")::text as BOOLEAN) as "bool", 
    CAST(("_airbyte_data":"integer")::text as NUMBER) as "integer", 
    CAST(("_airbyte_data":"float")::text as FLOAT) as "float", 
    CAST(("_airbyte_data":"date")::text as DATE) as "date", 
    CASE
      WHEN ("_airbyte_data":"ts_with_tz")::TEXT REGEXP '\\d{4}-\\d{2}-\\d{2}T(\\d{2}:){2}\\d{2}(\\+|-)\\d{4}'
        THEN TO_TIMESTAMP_TZ(("_airbyte_data":"ts_with_tz")::TEXT, 'YYYY-MM-DDTHH24:MI:SSTZHTZM')
      WHEN ("_airbyte_data":"ts_with_tz")::TEXT REGEXP '\\d{4}-\\d{2}-\\d{2}T(\\d{2}:){2}\\d{2}(\\+|-)\\d{2}'
        THEN TO_TIMESTAMP_TZ(("_airbyte_data":"ts_with_tz")::TEXT, 'YYYY-MM-DDTHH24:MI:SSTZH')
      WHEN ("_airbyte_data":"ts_with_tz")::TEXT REGEXP '\\d{4}-\\d{2}-\\d{2}T(\\d{2}:){2}\\d{2}\\.\\d{1,7}(\\+|-)\\d{4}'
        THEN TO_TIMESTAMP_TZ(("_airbyte_data":"ts_with_tz")::TEXT, 'YYYY-MM-DDTHH24:MI:SS.FFTZHTZM')
      WHEN ("_airbyte_data":"ts_with_tz")::TEXT REGEXP '\\d{4}-\\d{2}-\\d{2}T(\\d{2}:){2}\\d{2}\\.\\d{1,7}(\\+|-)\\d{2}'
        THEN TO_TIMESTAMP_TZ(("_airbyte_data":"ts_with_tz")::TEXT, 'YYYY-MM-DDTHH24:MI:SS.FFTZH')
      ELSE CAST(("_airbyte_data":"ts_with_tz")::TEXT AS TIMESTAMP_TZ)
    END as "ts_with_tz", 
    CAST(("_airbyte_data":"ts_without_tz")::text as TIMESTAMP_NTZ) as "ts_without_tz", 
    CASE 
      WHEN NOT (("_airbyte_data":"time_with_tz")::TEXT REGEXP '\\d{1,2}:\\d{2}:\\d{2}(\\.\\d+)?(Z|[+\\-]\\d{1,2}(:?\\d{2})?)') 
      THEN NULL 
      ELSE "_airbyte_data":"time_with_tz" 
    END as "time_with_tz", 
    CAST(("_airbyte_data":"time_no_tz")::text as TIME) as "time_no_tz", 
    CASE 
      WHEN TYPEOF("_airbyte_data":"array") != 'ARRAY' 
        THEN NULL 
      ELSE "_airbyte_data":"array" 
    END as "array", 
    CASE 
      WHEN TYPEOF("_airbyte_data":"json_object") != 'OBJECT'
        THEN NULL 
      ELSE "_airbyte_data":"json_object" 
    END as "json_object", 
    "_airbyte_raw_id", 
    TIMESTAMPADD(
      HOUR, 
      EXTRACT(timezone_hour from "_airbyte_extracted_at"), 
      TIMESTAMPADD(
        MINUTE,
        EXTRACT(timezone_minute from "_airbyte_extracted_at"),
        CONVERT_TIMEZONE('UTC', "_airbyte_extracted_at")
      )
    ) as "_airbyte_extracted_at", 
    "_airbyte_meta", 
    "_airbyte_generation_id", 
    ARRAY_COMPACT(
      ARRAY_CAT(
        CASE WHEN "_airbyte_meta":"changes" IS NOT NULL 
          THEN "_airbyte_meta":"changes" 
          ELSE ARRAY_CONSTRUCT()
        END,
        ARRAY_CONSTRUCT(
          CASE
            WHEN (TYPEOF("_airbyte_data":"primary_key") NOT IN ('NULL', 'NULL_VALUE'))
              AND (CAST(("_airbyte_data":"primary_key")::text as NUMBER) IS NULL)
              THEN OBJECT_CONSTRUCT('field', 'primary_key', 'change', 'NULLED', 'reason', 'DESTINATION_TYPECAST_ERROR')
            ELSE NULL
          END, 
          CASE
            WHEN (TYPEOF("_airbyte_data":"cursor") NOT IN ('NULL', 'NULL_VALUE'))
              AND (CAST(("_airbyte_data":"cursor")::text as TIMESTAMP_NTZ) IS NULL)
              THEN OBJECT_CONSTRUCT('field', 'cursor', 'change', 'NULLED', 'reason', 'DESTINATION_TYPECAST_ERROR')
            ELSE NULL
          END, 
          CASE
            WHEN (TYPEOF("_airbyte_data":"string") NOT IN ('NULL', 'NULL_VALUE'))
              AND ((("_airbyte_data":"string")::text) IS NULL)
              THEN OBJECT_CONSTRUCT('field', 'string', 'change', 'NULLED', 'reason', 'DESTINATION_TYPECAST_ERROR')
            ELSE NULL
          END, 
          CASE
            WHEN (TYPEOF("_airbyte_data":"bool") NOT IN ('NULL', 'NULL_VALUE'))
              AND (CAST(("_airbyte_data":"bool")::text as BOOLEAN) IS NULL)
              THEN OBJECT_CONSTRUCT('field', 'bool', 'change', 'NULLED', 'reason', 'DESTINATION_TYPECAST_ERROR')
            ELSE NULL
          END, 
          CASE
            WHEN (TYPEOF("_airbyte_data":"integer") NOT IN ('NULL', 'NULL_VALUE'))
              AND (CAST(("_airbyte_data":"integer")::text as NUMBER) IS NULL)
              THEN OBJECT_CONSTRUCT('field', 'integer', 'change', 'NULLED', 'reason', 'DESTINATION_TYPECAST_ERROR')
            ELSE NULL
          END, 
          CASE
            WHEN (TYPEOF("_airbyte_data":"float") NOT IN ('NULL', 'NULL_VALUE'))
              AND (CAST(("_airbyte_data":"float")::text as FLOAT) IS NULL)
              THEN OBJECT_CONSTRUCT('field', 'float', 'change', 'NULLED', 'reason', 'DESTINATION_TYPECAST_ERROR')
            ELSE NULL
          END, 
          CASE
            WHEN (TYPEOF("_airbyte_data":"date") NOT IN ('NULL', 'NULL_VALUE'))
              AND (CAST(("_airbyte_data":"date")::text as DATE) IS NULL)
              THEN OBJECT_CONSTRUCT('field', 'date', 'change', 'NULLED', 'reason', 'DESTINATION_TYPECAST_ERROR')
            ELSE NULL
          END, 
          CASE
            WHEN (TYPEOF("_airbyte_data":"ts_with_tz") NOT IN ('NULL', 'NULL_VALUE'))
              AND (CASE
            WHEN ("_airbyte_data":"ts_with_tz")::TEXT REGEXP '\\d{4}-\\d{2}-\\d{2}T(\\d{2}:){2}\\d{2}(\\+|-)\\d{4}'
              THEN TO_TIMESTAMP_TZ(("_airbyte_data":"ts_with_tz")::TEXT, 'YYYY-MM-DDTHH24:MI:SSTZHTZM')
            WHEN ("_airbyte_data":"ts_with_tz")::TEXT REGEXP '\\d{4}-\\d{2}-\\d{2}T(\\d{2}:){2}\\d{2}(\\+|-)\\d{2}'
              THEN TO_TIMESTAMP_TZ(("_airbyte_data":"ts_with_tz")::TEXT, 'YYYY-MM-DDTHH24:MI:SSTZH')
            WHEN ("_airbyte_data":"ts_with_tz")::TEXT REGEXP '\\d{4}-\\d{2}-\\d{2}T(\\d{2}:){2}\\d{2}\\.\\d{1,7}(\\+|-)\\d{4}'
              THEN TO_TIMESTAMP_TZ(("_airbyte_data":"ts_with_tz")::TEXT, 'YYYY-MM-DDTHH24:MI:SS.FFTZHTZM')
            WHEN ("_airbyte_data":"ts_with_tz")::TEXT REGEXP '\\d{4}-\\d{2}-\\d{2}T(\\d{2}:){2}\\d{2}\\.\\d{1,7}(\\+|-)\\d{2}'
              THEN TO_TIMESTAMP_TZ(("_airbyte_data":"ts_with_tz")::TEXT, 'YYYY-MM-DDTHH24:MI:SS.FFTZH')
            ELSE CAST(("_airbyte_data":"ts_with_tz")::TEXT AS TIMESTAMP_TZ)
          END IS NULL)
              THEN OBJECT_CONSTRUCT('field', 'ts_with_tz', 'change', 'NULLED', 'reason', 'DESTINATION_TYPECAST_ERROR')
            ELSE NULL
          END, 
          CASE
            WHEN (TYPEOF("_airbyte_data":"ts_without_tz") NOT IN ('NULL', 'NULL_VALUE'))
              AND (CAST(("_airbyte_data":"ts_without_tz")::text as TIMESTAMP_NTZ) IS NULL)
              THEN OBJECT_CONSTRUCT('field', 'ts_without_tz', 'change', 'NULLED', 'reason', 'DESTINATION_TYPECAST_ERROR')
            ELSE NULL
          END, 
          CASE
            WHEN (TYPEOF("_airbyte_data":"time_with_tz") NOT IN ('NULL', 'NULL_VALUE'))
              AND (CASE 
            WHEN NOT (("_airbyte_data":"time_with_tz")::TEXT REGEXP '\\d{1,2}:\\d{2}:\\d{2}(\\.\\d+)?(Z|[+\\-]\\d{1,2}(:?\\d{2})?)') 
            THEN NULL 
            ELSE "_airbyte_data":"time_with_tz" 
          END IS NULL)
              THEN OBJECT_CONSTRUCT('field', 'time_with_tz', 'change', 'NULLED', 'reason', 'DESTINATION_TYPECAST_ERROR')
            ELSE NULL
          END, 
          CASE
            WHEN (TYPEOF("_airbyte_data":"time_no_tz") NOT IN ('NULL', 'NULL_VALUE'))
              AND (CAST(("_airbyte_data":"time_no_tz")::text as TIME) IS NULL)
              THEN OBJECT_CONSTRUCT('field', 'time_no_tz', 'change', 'NULLED', 'reason', 'DESTINATION_TYPECAST_ERROR')
            ELSE NULL
          END, 
          CASE
            WHEN (TYPEOF("_airbyte_data":"array") NOT IN ('NULL', 'NULL_VALUE'))
              AND (CASE 
            WHEN TYPEOF("_airbyte_data":"array") != 'ARRAY' 
              THEN NULL 
            ELSE "_airbyte_data":"array" 
          END IS NULL)
              THEN OBJECT_CONSTRUCT('field', 'array', 'change', 'NULLED', 'reason', 'DESTINATION_TYPECAST_ERROR')
            ELSE NULL
          END, 
          CASE
            WHEN (TYPEOF("_airbyte_data":"json_object") NOT IN ('NULL', 'NULL_VALUE'))
              AND (CASE 
            WHEN TYPEOF("_airbyte_data":"json_object") != 'OBJECT'
              THEN NULL 
            ELSE "_airbyte_data":"json_object" 
          END IS NULL)
              THEN OBJECT_CONSTRUCT('field', 'json_object', 'change', 'NULLED', 'reason', 'DESTINATION_TYPECAST_ERROR')
            ELSE NULL
          END
        )
      )
    ) as "_airbyte_cast_errors"
  FROM 
    "PUBLIC"."old_raw_table_5mb_part1"
  WHERE 
    ("_airbyte_loaded_at" IS NULL ) 
), new_records AS (
  SELECT
    "primary_key", 
    "cursor", 
    "string", 
    "bool", 
    "integer", 
    "float", 
    "date", 
    "ts_with_tz", 
    "ts_without_tz", 
    "time_with_tz", 
    "time_no_tz", 
    "array", 
    "json_object", 
    "_airbyte_raw_id" as "_AIRBYTE_RAW_ID", 
    "_airbyte_extracted_at" as "_AIRBYTE_EXTRACTED_AT", 
    "_airbyte_generation_id" as "_AIRBYTE_GENERATION_ID", 
    CASE WHEN "_airbyte_meta" IS NOT NULL 
      THEN OBJECT_INSERT("_airbyte_meta", 'changes', "_airbyte_cast_errors", true) 
      ELSE OBJECT_CONSTRUCT('changes', "_airbyte_cast_errors") 
    END AS "_AIRBYTE_META",
    row_number() OVER (
      PARTITION BY "primary_key" ORDER BY "cursor" DESC NULLS LAST, "_AIRBYTE_EXTRACTED_AT" DESC
    ) AS row_number
  FROM intermediate_data
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
  "ts_without_tz", 
  "time_with_tz", 
  "time_no_tz", 
  "array", 
  "json_object", 
  _airbyte_raw_id, 
  _airbyte_extracted_at, 
  _airbyte_generation_id, 
  "_AIRBYTE_META"
FROM 
  new_records
WHERE row_number = 1;

DELETE FROM 
  "PUBLIC"."old_final_table_5mb"
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
        "PUBLIC"."old_final_table_5mb"
    )
    WHERE row_number != 1
  );

UPDATE "PUBLIC"."old_raw_table_5mb_part1" 
SET "_airbyte_loaded_at" = CURRENT_TIMESTAMP() 
WHERE "_airbyte_loaded_at" IS NULL;










-- "slow" T+D query -------------------------------
INSERT INTO "PUBLIC"."old_final_table_5mb"(
  "primary_key", 
  "cursor", 
  "string", 
  "bool", 
  "integer", 
  "float", 
  "date", 
  "ts_with_tz", 
  "ts_without_tz", 
  "time_with_tz", 
  "time_no_tz", 
  "array", 
  "json_object", 
  _airbyte_raw_id, 
  _airbyte_extracted_at, 
  _airbyte_generation_id,
  "_AIRBYTE_META"
)
WITH intermediate_data AS (
  SELECT
    TRY_CAST(("_airbyte_data":"primary_key")::text as NUMBER) as "primary_key", 
    TRY_CAST(("_airbyte_data":"cursor")::text as TIMESTAMP_NTZ) as "cursor", 
    (("_airbyte_data":"string")::text) as "string", 
    TRY_CAST(("_airbyte_data":"bool")::text as BOOLEAN) as "bool", 
    TRY_CAST(("_airbyte_data":"integer")::text as NUMBER) as "integer", 
    TRY_CAST(("_airbyte_data":"float")::text as FLOAT) as "float", 
    TRY_CAST(("_airbyte_data":"date")::text as DATE) as "date", 
    CASE
      WHEN ("_airbyte_data":"ts_with_tz")::TEXT REGEXP '\\d{4}-\\d{2}-\\d{2}T(\\d{2}:){2}\\d{2}(\\+|-)\\d{4}'
        THEN TO_TIMESTAMP_TZ(("_airbyte_data":"ts_with_tz")::TEXT, 'YYYY-MM-DDTHH24:MI:SSTZHTZM')
      WHEN ("_airbyte_data":"ts_with_tz")::TEXT REGEXP '\\d{4}-\\d{2}-\\d{2}T(\\d{2}:){2}\\d{2}(\\+|-)\\d{2}'
        THEN TO_TIMESTAMP_TZ(("_airbyte_data":"ts_with_tz")::TEXT, 'YYYY-MM-DDTHH24:MI:SSTZH')
      WHEN ("_airbyte_data":"ts_with_tz")::TEXT REGEXP '\\d{4}-\\d{2}-\\d{2}T(\\d{2}:){2}\\d{2}\\.\\d{1,7}(\\+|-)\\d{4}'
        THEN TO_TIMESTAMP_TZ(("_airbyte_data":"ts_with_tz")::TEXT, 'YYYY-MM-DDTHH24:MI:SS.FFTZHTZM')
      WHEN ("_airbyte_data":"ts_with_tz")::TEXT REGEXP '\\d{4}-\\d{2}-\\d{2}T(\\d{2}:){2}\\d{2}\\.\\d{1,7}(\\+|-)\\d{2}'
        THEN TO_TIMESTAMP_TZ(("_airbyte_data":"ts_with_tz")::TEXT, 'YYYY-MM-DDTHH24:MI:SS.FFTZH')
      ELSE TRY_CAST(("_airbyte_data":"ts_with_tz")::TEXT AS TIMESTAMP_TZ)
    END as "ts_with_tz", 
    TRY_CAST(("_airbyte_data":"ts_without_tz")::text as TIMESTAMP_NTZ) as "ts_without_tz", 
    CASE 
      WHEN NOT (("_airbyte_data":"time_with_tz")::TEXT REGEXP '\\d{1,2}:\\d{2}:\\d{2}(\\.\\d+)?(Z|[+\\-]\\d{1,2}(:?\\d{2})?)') 
      THEN NULL 
      ELSE "_airbyte_data":"time_with_tz" 
    END as "time_with_tz", 
    TRY_CAST(("_airbyte_data":"time_no_tz")::text as TIME) as "time_no_tz", 
    CASE 
      WHEN TYPEOF("_airbyte_data":"array") != 'ARRAY' 
        THEN NULL 
      ELSE "_airbyte_data":"array" 
    END as "array", 
    CASE 
      WHEN TYPEOF("_airbyte_data":"json_object") != 'OBJECT'
        THEN NULL 
      ELSE "_airbyte_data":"json_object" 
    END as "json_object", 
    "_airbyte_raw_id", 
    TIMESTAMPADD(
      HOUR, 
      EXTRACT(timezone_hour from "_airbyte_extracted_at"), 
      TIMESTAMPADD(
        MINUTE,
        EXTRACT(timezone_minute from "_airbyte_extracted_at"),
        CONVERT_TIMEZONE('UTC', "_airbyte_extracted_at")
      )
    ) as "_airbyte_extracted_at", 
    "_airbyte_meta", 
    "_airbyte_generation_id", 
    ARRAY_COMPACT(
      ARRAY_CAT(
        CASE WHEN "_airbyte_meta":"changes" IS NOT NULL 
          THEN "_airbyte_meta":"changes" 
          ELSE ARRAY_CONSTRUCT()
        END,
        ARRAY_CONSTRUCT(
          CASE
            WHEN (TYPEOF("_airbyte_data":"primary_key") NOT IN ('NULL', 'NULL_VALUE'))
              AND (TRY_CAST(("_airbyte_data":"primary_key")::text as NUMBER) IS NULL)
              THEN OBJECT_CONSTRUCT('field', 'primary_key', 'change', 'NULLED', 'reason', 'DESTINATION_TYPECAST_ERROR')
            ELSE NULL
          END, 
          CASE
            WHEN (TYPEOF("_airbyte_data":"cursor") NOT IN ('NULL', 'NULL_VALUE'))
              AND (TRY_CAST(("_airbyte_data":"cursor")::text as TIMESTAMP_NTZ) IS NULL)
              THEN OBJECT_CONSTRUCT('field', 'cursor', 'change', 'NULLED', 'reason', 'DESTINATION_TYPECAST_ERROR')
            ELSE NULL
          END, 
          CASE
            WHEN (TYPEOF("_airbyte_data":"string") NOT IN ('NULL', 'NULL_VALUE'))
              AND ((("_airbyte_data":"string")::text) IS NULL)
              THEN OBJECT_CONSTRUCT('field', 'string', 'change', 'NULLED', 'reason', 'DESTINATION_TYPECAST_ERROR')
            ELSE NULL
          END, 
          CASE
            WHEN (TYPEOF("_airbyte_data":"bool") NOT IN ('NULL', 'NULL_VALUE'))
              AND (TRY_CAST(("_airbyte_data":"bool")::text as BOOLEAN) IS NULL)
              THEN OBJECT_CONSTRUCT('field', 'bool', 'change', 'NULLED', 'reason', 'DESTINATION_TYPECAST_ERROR')
            ELSE NULL
          END, 
          CASE
            WHEN (TYPEOF("_airbyte_data":"integer") NOT IN ('NULL', 'NULL_VALUE'))
              AND (TRY_CAST(("_airbyte_data":"integer")::text as NUMBER) IS NULL)
              THEN OBJECT_CONSTRUCT('field', 'integer', 'change', 'NULLED', 'reason', 'DESTINATION_TYPECAST_ERROR')
            ELSE NULL
          END, 
          CASE
            WHEN (TYPEOF("_airbyte_data":"float") NOT IN ('NULL', 'NULL_VALUE'))
              AND (TRY_CAST(("_airbyte_data":"float")::text as FLOAT) IS NULL)
              THEN OBJECT_CONSTRUCT('field', 'float', 'change', 'NULLED', 'reason', 'DESTINATION_TYPECAST_ERROR')
            ELSE NULL
          END, 
          CASE
            WHEN (TYPEOF("_airbyte_data":"date") NOT IN ('NULL', 'NULL_VALUE'))
              AND (TRY_CAST(("_airbyte_data":"date")::text as DATE) IS NULL)
              THEN OBJECT_CONSTRUCT('field', 'date', 'change', 'NULLED', 'reason', 'DESTINATION_TYPECAST_ERROR')
            ELSE NULL
          END, 
          CASE
            WHEN (TYPEOF("_airbyte_data":"ts_with_tz") NOT IN ('NULL', 'NULL_VALUE'))
              AND (CASE
            WHEN ("_airbyte_data":"ts_with_tz")::TEXT REGEXP '\\d{4}-\\d{2}-\\d{2}T(\\d{2}:){2}\\d{2}(\\+|-)\\d{4}'
              THEN TO_TIMESTAMP_TZ(("_airbyte_data":"ts_with_tz")::TEXT, 'YYYY-MM-DDTHH24:MI:SSTZHTZM')
            WHEN ("_airbyte_data":"ts_with_tz")::TEXT REGEXP '\\d{4}-\\d{2}-\\d{2}T(\\d{2}:){2}\\d{2}(\\+|-)\\d{2}'
              THEN TO_TIMESTAMP_TZ(("_airbyte_data":"ts_with_tz")::TEXT, 'YYYY-MM-DDTHH24:MI:SSTZH')
            WHEN ("_airbyte_data":"ts_with_tz")::TEXT REGEXP '\\d{4}-\\d{2}-\\d{2}T(\\d{2}:){2}\\d{2}\\.\\d{1,7}(\\+|-)\\d{4}'
              THEN TO_TIMESTAMP_TZ(("_airbyte_data":"ts_with_tz")::TEXT, 'YYYY-MM-DDTHH24:MI:SS.FFTZHTZM')
            WHEN ("_airbyte_data":"ts_with_tz")::TEXT REGEXP '\\d{4}-\\d{2}-\\d{2}T(\\d{2}:){2}\\d{2}\\.\\d{1,7}(\\+|-)\\d{2}'
              THEN TO_TIMESTAMP_TZ(("_airbyte_data":"ts_with_tz")::TEXT, 'YYYY-MM-DDTHH24:MI:SS.FFTZH')
            ELSE TRY_CAST(("_airbyte_data":"ts_with_tz")::TEXT AS TIMESTAMP_TZ)
          END IS NULL)
              THEN OBJECT_CONSTRUCT('field', 'ts_with_tz', 'change', 'NULLED', 'reason', 'DESTINATION_TYPECAST_ERROR')
            ELSE NULL
          END, 
          CASE
            WHEN (TYPEOF("_airbyte_data":"ts_without_tz") NOT IN ('NULL', 'NULL_VALUE'))
              AND (TRY_CAST(("_airbyte_data":"ts_without_tz")::text as TIMESTAMP_NTZ) IS NULL)
              THEN OBJECT_CONSTRUCT('field', 'ts_without_tz', 'change', 'NULLED', 'reason', 'DESTINATION_TYPECAST_ERROR')
            ELSE NULL
          END, 
          CASE
            WHEN (TYPEOF("_airbyte_data":"time_with_tz") NOT IN ('NULL', 'NULL_VALUE'))
              AND (CASE 
            WHEN NOT (("_airbyte_data":"time_with_tz")::TEXT REGEXP '\\d{1,2}:\\d{2}:\\d{2}(\\.\\d+)?(Z|[+\\-]\\d{1,2}(:?\\d{2})?)') 
            THEN NULL 
            ELSE "_airbyte_data":"time_with_tz" 
          END IS NULL)
              THEN OBJECT_CONSTRUCT('field', 'time_with_tz', 'change', 'NULLED', 'reason', 'DESTINATION_TYPECAST_ERROR')
            ELSE NULL
          END, 
          CASE
            WHEN (TYPEOF("_airbyte_data":"time_no_tz") NOT IN ('NULL', 'NULL_VALUE'))
              AND (TRY_CAST(("_airbyte_data":"time_no_tz")::text as TIME) IS NULL)
              THEN OBJECT_CONSTRUCT('field', 'time_no_tz', 'change', 'NULLED', 'reason', 'DESTINATION_TYPECAST_ERROR')
            ELSE NULL
          END, 
          CASE
            WHEN (TYPEOF("_airbyte_data":"array") NOT IN ('NULL', 'NULL_VALUE'))
              AND (CASE 
            WHEN TYPEOF("_airbyte_data":"array") != 'ARRAY' 
              THEN NULL 
            ELSE "_airbyte_data":"array" 
          END IS NULL)
              THEN OBJECT_CONSTRUCT('field', 'array', 'change', 'NULLED', 'reason', 'DESTINATION_TYPECAST_ERROR')
            ELSE NULL
          END, 
          CASE
            WHEN (TYPEOF("_airbyte_data":"json_object") NOT IN ('NULL', 'NULL_VALUE'))
              AND (CASE 
            WHEN TYPEOF("_airbyte_data":"json_object") != 'OBJECT'
              THEN NULL 
            ELSE "_airbyte_data":"json_object" 
          END IS NULL)
              THEN OBJECT_CONSTRUCT('field', 'json_object', 'change', 'NULLED', 'reason', 'DESTINATION_TYPECAST_ERROR')
            ELSE NULL
          END
        )
      )
    ) as "_airbyte_cast_errors"
  FROM 
    "PUBLIC"."old_raw_table_5mb_part1"
  WHERE 
    ("_airbyte_loaded_at" IS NULL ) 
), new_records AS (
  SELECT
    "primary_key", 
    "cursor", 
    "string", 
    "bool", 
    "integer", 
    "float", 
    "date", 
    "ts_with_tz", 
    "ts_without_tz", 
    "time_with_tz", 
    "time_no_tz", 
    "array", 
    "json_object", 
    "_airbyte_raw_id" as "_AIRBYTE_RAW_ID", 
    "_airbyte_extracted_at" as "_AIRBYTE_EXTRACTED_AT", 
    "_airbyte_generation_id" as "_AIRBYTE_GENERATION_ID", 
    CASE WHEN "_airbyte_meta" IS NOT NULL 
      THEN OBJECT_INSERT("_airbyte_meta", 'changes', "_airbyte_cast_errors", true) 
      ELSE OBJECT_CONSTRUCT('changes', "_airbyte_cast_errors") 
    END AS "_AIRBYTE_META",
    row_number() OVER (
      PARTITION BY "primary_key" ORDER BY "cursor" DESC NULLS LAST, "_AIRBYTE_EXTRACTED_AT" DESC
    ) AS row_number
  FROM intermediate_data
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
  "ts_without_tz", 
  "time_with_tz", 
  "time_no_tz", 
  "array", 
  "json_object", 
  _airbyte_raw_id, 
  _airbyte_extracted_at, 
  _airbyte_generation_id, 
  "_AIRBYTE_META"
FROM 
  new_records
WHERE row_number = 1;

DELETE FROM 
  "PUBLIC"."old_final_table_5mb"
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
        "PUBLIC"."old_final_table_5mb"
    )
    WHERE row_number != 1
  );

UPDATE "PUBLIC"."old_raw_table_5mb_part1" 
SET "_airbyte_loaded_at" = CURRENT_TIMESTAMP() 
WHERE "_airbyte_loaded_at" IS NULL;
