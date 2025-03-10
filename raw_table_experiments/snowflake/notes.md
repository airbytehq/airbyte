## Snowflake

Raw table create logic is [here](https://github.com/airbytehq/airbyte/blob/7ba3e2dabccb9d7a0491f3e472994a5ae83ac73f/airbyte-integrations/connectors/destination-snowflake/src/main/kotlin/io/airbyte/integrations/destination/snowflake/operation/SnowflakeStorageOperation.kt#L106-L117)
with some elements in [here](https://github.com/airbytehq/airbyte/blob/5b9ddb16cb861df2085c5baa53ec035c9485a786/airbyte-integrations/connectors/destination-snowflake/src/main/kotlin/io/airbyte/integrations/destination/snowflake/typing_deduping/SnowflakeSqlGenerator.kt#L33)

In order to create the input tables, we have to create storage and stage objects:

```sql
create or replace storage integration no_raw_table_storage_10mb
    type = external_stage
    storage_provider = gcs
    enabled = true
    storage_allowed_locations = ( 'gcs://no_raw_tables/10mb_noheader.csv');
    
CREATE OR REPLACE FILE FORMAT my_csv_format
  TYPE = CSV
  FIELD_DELIMITER = ','
  SKIP_HEADER = 0
  -- This is key: indicates that fields may be enclosed in double quotes
  FIELD_OPTIONALLY_ENCLOSED_BY = '"'
  ESCAPE = '\\';

CREATE OR REPLACE STAGE no_raw_table_stage_10mb
    STORAGE_INTEGRATION = no_raw_table_storage_10mb
    URL = 'gcs://no_raw_tables/10mb_noheader.csv'
    FILE_FORMAT = my_csv_format;
  
CREATE OR REPLACE TABLE no_raw_table_10mb (
    primary_key      NUMBER(38,0),     -- e.g. 1
    cursor           TIMESTAMP_NTZ,    -- e.g. 2025-01-01T12:00:00
    string           VARCHAR,          -- e.g. OehNMSOA
    bool             BOOLEAN,          -- e.g. True
    integer          NUMBER(38,0),     -- e.g. 705
    float            FLOAT,            -- e.g. 535.38
    date             DATE,             -- e.g. 2020-09-28
    ts_with_tz       TIMESTAMP_TZ,     -- e.g. 2017-01-23T21:10:56+01:00
    ts_no_tz         TIMESTAMP_NTZ,    -- e.g. 2013-07-21T09:51:47
    -- Snowflake does not have a TIME WITH TIME ZONE type, so we store that as VARCHAR
    time_with_tz     VARCHAR,          -- e.g. 03:46:04+02:00
    time_no_tz       TIME,             -- e.g. 05:37:33
    -- Use VARIANT for semi-structured data like arrays and JSON
    array            VARIANT,          -- e.g. [16]
    json_object      VARIANT           -- e.g. {"id":7544,"name":"pXOnAZ","active":true,"score":6.82}
);

COPY INTO no_raw_table_10mb
FROM @no_raw_table_stage_10mb
FILE_FORMAT = my_csv_format;
```

Then, we are creating the sub tables based on the original input table:

```sql
CREATE TABLE input_typed_data_part1 LIKE no_raw_table_10mb;
CREATE TABLE input_typed_data_part2 LIKE no_raw_table_10mb;

INSERT INTO input_typed_data_part1 (
    primary_key,
    cursor,
    string,
    bool,
    integer,
    float,
    date,
    ts_with_tz,
    ts_no_tz,
    time_with_tz,
    time_no_tz,
    array,
    json_object
)
SELECT 
    primary_key,
    cursor,
    string,
    bool,
    integer,
    float,
    date,
    ts_with_tz,
    ts_no_tz,
    time_with_tz,
    time_no_tz,
    array,
    json_object
FROM (
    SELECT *, ROW_NUMBER() OVER (ORDER BY RANDOM()) AS row_num
    FROM no_raw_table_10mb
)
WHERE MOD(row_num, 2) = 1;
----
INSERT INTO input_typed_data_part2 (
    primary_key,
    cursor,
    string,
    bool,
    integer,
    float,
    date,
    ts_with_tz,
    ts_no_tz,
    time_with_tz,
    time_no_tz,
    array,
    json_object
)
SELECT 
    primary_key,
    cursor,
    string,
    bool,
    integer,
    float,
    date,
    ts_with_tz,
    ts_no_tz,
    time_with_tz,
    time_no_tz,
    array,
    json_object
FROM (
    SELECT *, ROW_NUMBER() OVER (ORDER BY RANDOM()) AS row_num
    FROM no_raw_table_10mb
)
WHERE MOD(row_num, 2) = 0;
```

Then to create the old style 2 tables based on the input table we can run the following:

```sql
-- Create the first table
CREATE OR REPLACE TABLE old_raw_table_5mb_part1 (
  _airbyte_raw_id VARCHAR,
  _airbyte_extracted_at TIMESTAMP_TZ,
  _airbyte_loaded_at TIMESTAMP_TZ,
  _airbyte_data VARCHAR,
  _airbyte_meta VARCHAR,
  _airbyte_generation_id NUMBER(38,0)
)
AS 
SELECT
  UUID_STRING(), -- Snowflake's UUID generator
  ts_with_tz,
  NULL,
  OBJECT_CONSTRUCT(
    'primary_key', t.primary_key,
    'cursor', t.cursor,
    'string', t.string,
    'bool', t.bool,
    'integer', t.integer,
    'float', t.float,
    'date', t.date,
    'ts_with_tz', t.ts_with_tz,
    'ts_no_tz', t.ts_no_tz,
    'time_with_tz', t.time_with_tz,
    'time_no_tz', t.time_no_tz,
    'array', t.array,
    'json_object', t.json_object
  )::VARCHAR, -- Convert constructed object to JSON string
  '{"changes":[],"sync_id":42}',
  42
FROM NO_RAW_TABLE.PUBLIC.input_typed_data_part1 AS t;

-- Create the second table
CREATE OR REPLACE TABLE old_raw_table_5mb_part2 (
  _airbyte_raw_id VARCHAR,
  _airbyte_extracted_at TIMESTAMP_TZ,
  _airbyte_loaded_at TIMESTAMP_TZ,
  _airbyte_data VARCHAR,
  _airbyte_meta VARCHAR,
  _airbyte_generation_id NUMBER(38,0)
)
AS 
SELECT
  UUID_STRING(), -- Snowflake's UUID generator
  ts_with_tz,
  NULL,
  OBJECT_CONSTRUCT(
    'primary_key', t.primary_key,
    'cursor', t.cursor,
    'string', t.string,
    'bool', t.bool,
    'integer', t.integer,
    'float', t.float,
    'date', t.date,
    'ts_with_tz', t.ts_with_tz,
    'ts_no_tz', t.ts_no_tz,
    'time_with_tz', t.time_with_tz,
    'time_no_tz', t.time_no_tz,
    'array', t.array,
    'json_object', t.json_object
  )::VARCHAR, -- Convert constructed object to JSON string
  '{"changes":[],"sync_id":42}',
  42
FROM NO_RAW_TABLE.PUBLIC.input_typed_data_part2 AS t;
```

And finally, to create the new style input tables:

```sql
CREATE OR REPLACE TABLE no_raw_table.public."new_input_table_50gb_part1" (
    "_AIRBYTE_RAW_ID"         VARCHAR,
    "_AIRBYTE_EXTRACTED_AT"   TIMESTAMP_TZ,
    "_AIRBYTE_META"           VARIANT,
    "_AIRBYTE_GENERATION_ID"  NUMBER(38, 0),
    "primary_key"             NUMBER(38, 0),
    "cursor"                  TIMESTAMP_NTZ,
    "string"                  VARCHAR,
    "bool"                    BOOLEAN,
    "integer"                 NUMBER(38, 0),
    "float"                   NUMBER(38, 9),
    "date"                    DATE,
    "ts_with_tz"              TIMESTAMP_TZ,
    "ts_no_tz"                TIMESTAMP_NTZ,
    "time_with_tz"            STRING,
    "time_no_tz"              TIME,
    "array"                   VARIANT,
    "json_object"             VARIANT
);

-- Insert into the new table from part1
INSERT INTO no_raw_table.public."new_input_table_50gb_part1"
SELECT
    UUID_STRING()                                 AS "_AIRBYTE_RAW_ID",
    t.ts_with_tz                                  AS "_AIRBYTE_EXTRACTED_AT",
    PARSE_JSON('{"changes":[],"sync_id":42}')     AS "_AIRBYTE_META",
    42                                            AS "_AIRBYTE_GENERATION_ID",
    t.primary_key         AS "primary_key",
    t.cursor              AS "cursor",
    t.string              AS "string",
    t.bool                AS "bool",
    t.integer             AS "integer",
    t.float               AS "float",
    t.date                AS "date",
    t.ts_with_tz          AS "ts_with_tz",
    t.ts_no_tz            AS "ts_no_tz",
    t.time_with_tz        AS "time_with_tz",
    t.time_no_tz          AS "time_no_tz",
    t.array               AS "array",
    t.json_object         AS "json_object"
FROM no_raw_table.public.input_typed_data_50gb_part1 AS t;


CREATE OR REPLACE TABLE no_raw_table.public."new_input_table_50gb_part2" (
    "_AIRBYTE_RAW_ID"         VARCHAR,
    "_AIRBYTE_EXTRACTED_AT"   TIMESTAMP_TZ,
    "_AIRBYTE_META"           VARIANT,
    "_AIRBYTE_GENERATION_ID"  NUMBER(38, 0),
    "primary_key"             NUMBER(38, 0),
    "cursor"                  TIMESTAMP_NTZ,
    "string"                  VARCHAR,
    "bool"                    BOOLEAN,
    "integer"                 NUMBER(38, 0),
    "float"                   NUMBER(38, 9),
    "date"                    DATE,
    "ts_with_tz"              TIMESTAMP_TZ,
    "ts_no_tz"                TIMESTAMP_NTZ,
    "time_with_tz"            STRING,
    "time_no_tz"              TIME,
    "array"                   VARIANT,
    "json_object"             VARIANT
);

-- Insert into the new table from part2
INSERT INTO no_raw_table.public."new_input_table_50gb_part2"
SELECT
    UUID_STRING()                                 AS "_AIRBYTE_RAW_ID",
    t.ts_with_tz                                  AS "_AIRBYTE_EXTRACTED_AT",
    PARSE_JSON('{"changes":[],"sync_id":42}')     AS "_AIRBYTE_META",
    42                                            AS "_AIRBYTE_GENERATION_ID",
    t.primary_key         AS "primary_key",
    t.cursor              AS "cursor",
    t.string              AS "string",
    t.bool                AS "bool",
    t.integer             AS "integer",
    t.float               AS "float",
    t.date                AS "date",
    t.ts_with_tz          AS "ts_with_tz",
    t.ts_no_tz            AS "ts_no_tz",
    t.time_with_tz        AS "time_with_tz",
    t.time_no_tz          AS "time_no_tz",
    t.array               AS "array",
    t.json_object         AS "json_object"
FROM no_raw_table.public.input_typed_data_50gb_part2 AS t;
```