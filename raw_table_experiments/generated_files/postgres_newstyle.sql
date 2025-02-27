-- naive create table --------------------------------
DROP TABLE IF EXISTS no_raw_tables_experiment.new_final_table_5gb;
create table "no_raw_tables_experiment"."new_final_table_5gb" (
  "_airbyte_raw_id" varchar(36) not null,
  "_airbyte_extracted_at" timestamp with time zone not null,
  "_airbyte_generation_id" bigint,
  "_airbyte_meta" jsonb not null,
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










-- "naive" dedup query -------------------------------
insert into
  "no_raw_tables_experiment"."new_final_table_5gb" (
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
    "_airbyte_raw_id",
    "_airbyte_extracted_at",
    "_airbyte_generation_id",
    "_airbyte_meta"
  )
with "numbered_rows" as (
  select
    *,
    row_number() over (partition by "primary_key" order by "cursor" desc NULLS LAST, "_airbyte_extracted_at" desc) as "row_number"
  from "no_raw_tables_experiment"."new_input_table_5gb_part1"
)
select
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
  "_airbyte_raw_id",
  "_airbyte_extracted_at",
  "_airbyte_generation_id",
  "_airbyte_meta"
from "numbered_rows"
where "row_number" = 1;
delete from "no_raw_tables_experiment"."new_final_table_5gb"
where
  "_airbyte_raw_id" in (
    select
      "_airbyte_raw_id"
    from
      (
        select
          "_airbyte_raw_id",
          row_number() over (
            partition by "primary_key"
            order by
              "cursor" desc NULLS LAST,
              "_airbyte_extracted_at" desc
          ) as "row_number"
        from
          "no_raw_tables_experiment"."new_final_table_5gb"
      ) as "airbyte_ids"
    where
      "row_number" <> 1
  );
