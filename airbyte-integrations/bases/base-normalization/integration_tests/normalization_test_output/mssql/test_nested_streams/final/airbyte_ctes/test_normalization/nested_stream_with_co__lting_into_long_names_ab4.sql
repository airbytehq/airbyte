USE [test_normalization];
    execute('create view _airbyte_test_normalization."nested_stream_with_co__lting_into_long_names_ab4__dbt_tmp" as
    
-- SQL model to prepare for deduplicating records based on the hash record column
select
  row_number() over (
    partition by _airbyte_nested_strea__nto_long_names_hashid
    order by _airbyte_emitted_at asc
  ) as _airbyte_row_num,
  tmp.*
from "test_normalization"._airbyte_test_normalization."nested_stream_with_co__lting_into_long_names_ab3" tmp
-- nested_stream_with_co__lting_into_long_names from "test_normalization".test_normalization._airbyte_raw_nested_stream_with_complex_columns_resulting_into_long_names
    ');

