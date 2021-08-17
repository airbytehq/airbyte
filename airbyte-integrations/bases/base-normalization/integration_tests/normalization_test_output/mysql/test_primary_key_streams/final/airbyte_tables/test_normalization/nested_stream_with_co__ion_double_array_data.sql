

  create  table
    test_normalization.`nested_stream_with_co__ion_double_array_data__dbt_tmp`
  as (
    
-- Final base SQL model
select
    _airbyte_partition_hashid,
    id,
    _airbyte_emitted_at,
    _airbyte_double_array_data_hashid
from _airbyte_test_normalization.`nested_stream_with_co_3double_array_data_ab3`
-- double_array_data at nested_stream_with_complex_columns_resulting_into_long_names/partition/double_array_data from test_normalization.`nested_stream_with_co___long_names_partition`
  )
