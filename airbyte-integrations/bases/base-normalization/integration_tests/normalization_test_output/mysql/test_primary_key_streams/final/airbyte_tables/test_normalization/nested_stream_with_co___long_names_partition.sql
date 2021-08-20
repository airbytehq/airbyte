

  create  table
    test_normalization.`nested_stream_with_co___long_names_partition__dbt_tmp`
  as (
    
-- Final base SQL model
select
    _airbyte_nested_strea__nto_long_names_hashid,
    double_array_data,
    `DATA`,
    `column__'with"_quotes`,
    _airbyte_emitted_at,
    _airbyte_partition_hashid
from _airbyte_test_normalization.`nested_stream_with_co_2g_names_partition_ab3`
-- partition at nested_stream_with_complex_columns_resulting_into_long_names/partition from test_normalization.`nested_stream_with_co__lting_into_long_names`
  )
