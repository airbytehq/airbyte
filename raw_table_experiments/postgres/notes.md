## postgres

raw table create logic is [here](https://github.com/airbytehq/airbyte/blob/86aad30849a4f2ba5fd60efc53650ba9956d7f34/airbyte-cdk/java/airbyte-cdk/db-destinations/src/main/kotlin/io/airbyte/cdk/integrations/destination/jdbc/JdbcSqlOperations.kt#L112),
and [here](https://github.com/airbytehq/airbyte/blob/86aad30849a4f2ba5fd60efc53650ba9956d7f34/airbyte-integrations/connectors/destination-postgres/src/main/kotlin/io/airbyte/integrations/destination/postgres/PostgresSqlOperations.kt#L29)

equivalent:
```sql
CREATE TABLE IF NOT EXISTS no_raw_tables_experiment.raw_table_10mb (
  _airbyte_raw_id VARCHAR PRIMARY KEY,
  _airbyte_data JSONB,
  _airbyte_extracted_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
  _airbyte_loaded_at TIMESTAMP WITH TIME ZONE DEFAULT NULL,
  _airbyte_meta JSONB,
  _airbyte_generation_id BIGINT
);
CREATE INDEX IF NOT EXISTS raw_table_10mb_raw_id ON no_raw_tables_experiment.raw_table_10mb(_airbyte_raw_id)
CREATE INDEX IF NOT EXISTS raw_table_10mb_extracted_at ON no_raw_tables_experiment.raw_table_10mb(_airbyte_extracted_at)
CREATE INDEX IF NOT EXISTS raw_table_10mb_loaded_at ON no_raw_tables_experiment.raw_table_10mb(_airbyte_loaded_at, _airbyte_extracted_at)
```

test setup:
```sql
create schema if not exists no_raw_tables_experiment;
drop table if exists no_raw_tables_experiment.input_typed_data_10mb;
create table no_raw_tables_experiment.input_typed_data_10mb (
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
  'gs://no_raw_tables/10mb_noheader.csv' \
  --database postgres \
  --table no_raw_tables_experiment.input_typed_data_10mb
```
