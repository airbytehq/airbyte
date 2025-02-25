## postgres

raw table create logic is [here](https://github.com/airbytehq/airbyte/blob/86aad30849a4f2ba5fd60efc53650ba9956d7f34/airbyte-cdk/java/airbyte-cdk/db-destinations/src/main/kotlin/io/airbyte/cdk/integrations/destination/jdbc/JdbcSqlOperations.kt#L112),
and [here](https://github.com/airbytehq/airbyte/blob/86aad30849a4f2ba5fd60efc53650ba9956d7f34/airbyte-integrations/connectors/destination-postgres/src/main/kotlin/io/airbyte/integrations/destination/postgres/PostgresSqlOperations.kt#L29)

equivalent:
```sql
CREATE TABLE IF NOT EXISTS no_raw_tables_experiment.raw_table_50gb (
  _airbyte_raw_id VARCHAR PRIMARY KEY,
  _airbyte_data JSONB,
  _airbyte_extracted_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
  _airbyte_loaded_at TIMESTAMP WITH TIME ZONE DEFAULT NULL,
  _airbyte_meta JSONB,
  _airbyte_generation_id BIGINT
);
CREATE INDEX IF NOT EXISTS raw_table_50gb_raw_id ON no_raw_tables_experiment.raw_table_50gb(_airbyte_raw_id)
CREATE INDEX IF NOT EXISTS raw_table_50gb_extracted_at ON no_raw_tables_experiment.raw_table_50gb(_airbyte_extracted_at)
CREATE INDEX IF NOT EXISTS raw_table_50gb_loaded_at ON no_raw_tables_experiment.raw_table_50gb(_airbyte_loaded_at, _airbyte_extracted_at)
```

test setup:
```sql
create schema if not exists no_raw_tables_experiment;
drop table if exists no_raw_tables_experiment.input_typed_data_full;
create table no_raw_tables_experiment.input_typed_data_full (
  "primary_key" bigint,
  "cursor" timestamp,
  "string" varchar,
  "bool" boolean,
  "integer" bigint,
  "float" decimal(38, 9),
  "date" date,
  "ts_with_tz" timestamp with time zone,
  "ts_without_tz" timestamp,
  "time_with_tz" time with time zone,
  "time_no_tz" time,
  "array" jsonb,
  "json_object" jsonb
);

```

```shell
gcloud --project dataline-integration-testing sql import csv \
  no-raw-table-experiment \
  'gs://no_raw_tables/data_export_100GB_final.csv' \
  --database postgres \
  --table no_raw_tables_experiment.input_typed_data_full
```

```sql
DROP TABLE IF EXISTS no_raw_tables_experiment.input_typed_data_part1;
CREATE TABLE no_raw_tables_experiment.input_typed_data_part1
AS SELECT * FROM no_raw_tables_experiment.input_typed_data_full
  WHERE "string" >= 'M';
DROP TABLE IF EXISTS no_raw_tables_experiment.input_typed_data_part2;
CREATE TABLE no_raw_tables_experiment.input_typed_data_part2
AS SELECT * FROM no_raw_tables_experiment.input_typed_data_full
  WHERE "string" <= 'm';

CREATE TABLE no_raw_tables_experiment.old_raw_table_50gb_part1 (
  _airbyte_raw_id VARCHAR PRIMARY KEY,
  _airbyte_data JSONB,
  _airbyte_extracted_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
  _airbyte_loaded_at TIMESTAMP WITH TIME ZONE DEFAULT NULL,
  _airbyte_meta JSONB,
  _airbyte_generation_id BIGINT
);
CREATE INDEX old_raw_table_50gb_part1_raw_id ON no_raw_tables_experiment.old_raw_table_50gb_part1(_airbyte_raw_id);
CREATE INDEX old_raw_table_50gb_part1_extracted_at ON no_raw_tables_experiment.old_raw_table_50gb_part1(_airbyte_extracted_at);
CREATE INDEX old_raw_table_50gb_part1_loaded_at ON no_raw_tables_experiment.old_raw_table_50gb_part1(_airbyte_loaded_at, _airbyte_extracted_at);
INSERT INTO no_raw_tables_experiment.old_raw_table_50gb_part1
SELECT
  gen_random_uuid(),
  row_to_json(t),
  ts_with_tz,
  cast(null as timestamp),
  '{"changes":[],"sync_id":42}' :: jsonb,
  42
FROM no_raw_tables_experiment.input_typed_data_part1 t;

CREATE TABLE no_raw_tables_experiment.old_raw_table_50gb_part2 (
  _airbyte_raw_id VARCHAR PRIMARY KEY,
  _airbyte_data JSONB,
  _airbyte_extracted_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
  _airbyte_loaded_at TIMESTAMP WITH TIME ZONE DEFAULT NULL,
  _airbyte_meta JSONB,
  _airbyte_generation_id BIGINT
);
CREATE INDEX old_raw_table_50gb_part2_raw_id ON no_raw_tables_experiment.old_raw_table_50gb_part2(_airbyte_raw_id);
CREATE INDEX old_raw_table_50gb_part2_extracted_at ON no_raw_tables_experiment.old_raw_table_50gb_part2(_airbyte_extracted_at);
CREATE INDEX old_raw_table_50gb_part2_loaded_at ON no_raw_tables_experiment.old_raw_table_50gb_part2(_airbyte_loaded_at, _airbyte_extracted_at);
INSERT INTO no_raw_tables_experiment.old_raw_table_50gb_part2
SELECT
  gen_random_uuid(),
  row_to_json(t),
  ts_with_tz,
  cast(null as timestamp),
  '{"changes":[],"sync_id":42}' :: jsonb,
  42
FROM no_raw_tables_experiment.input_typed_data_part2 t;

CREATE TABLE no_raw_tables_experiment.new_input_table_50gb_part1 (
  _airbyte_raw_id varchar,
  _airbyte_extracted_at timestamp with time zone,
  _airbyte_meta jsonb,
  _airbyte_generation_id bigint,
  "primary_key" bigint,
  "cursor" timestamp,
  "string" varchar,
  "bool" boolean,
  "integer" bigint,
  "float" decimal(38, 9),
  "date" date,
  "ts_with_tz" timestamp with time zone,
  "ts_without_tz" timestamp,
  "time_with_tz" time with time zone,
  "time_no_tz" time,
  "array" jsonb,
  "json_object" jsonb
);
INSERT INTO no_raw_tables_experiment.new_input_table_50gb_part1
SELECT
  gen_random_uuid(),
  ts_with_tz,
  '{"changes":[],"sync_id":42}' :: jsonb,
  42,
  *
FROM no_raw_tables_experiment.input_typed_data_part1 AS t;

CREATE TABLE no_raw_tables_experiment.new_input_table_50gb_part2 (
  _airbyte_raw_id varchar,
  _airbyte_extracted_at timestamp with time zone,
  _airbyte_meta jsonb,
  _airbyte_generation_id bigint,
  "primary_key" bigint,
  "cursor" timestamp,
  "string" varchar,
  "bool" boolean,
  "integer" bigint,
  "float" decimal(38, 9),
  "date" date,
  "ts_with_tz" timestamp with time zone,
  "ts_without_tz" timestamp,
  "time_with_tz" time with time zone,
  "time_no_tz" time,
  "array" jsonb,
  "json_object" jsonb
);
INSERT INTO no_raw_tables_experiment.new_input_table_50gb_part2
SELECT
  gen_random_uuid(),
  ts_with_tz,
  '{"changes":[],"sync_id":42}' :: jsonb,
  42,
  *
FROM no_raw_tables_experiment.input_typed_data_part2 AS t;
```
