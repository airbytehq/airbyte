

  create  table "postgres".test_normalization."nested_stream_with_c__lting_into_long_names_scd__dbt_tmp"
  as (
    
-- SQL model to build a Type 2 Slowly Changing Dimension (SCD) table for each record identified by their primary key
select
    "id",
    "date",
    "partition",
  "date" as _airbyte_start_at,
  lag("date") over (
    partition by "id"
    order by "date" is null asc, "date" desc, _airbyte_emitted_at desc
  ) as _airbyte_end_at,
  case when lag("date") over (
    partition by "id"
    order by "date" is null asc, "date" desc, _airbyte_emitted_at desc
  ) is null  then 1 else 0 end as _airbyte_active_row,
  _airbyte_emitted_at,
  _airbyte_nested_stre__nto_long_names_hashid
from "postgres"._airbyte_test_normalization."nested_stream_with_c__lting_into_long_names_ab4"
-- nested_stream_with_c__lting_into_long_names from "postgres".test_normalization._airbyte_raw_nested_stream_with_complex_columns_resulting_into_long_names
where _airbyte_row_num = 1
  );