

  create or replace table `dataline-integration-testing`.test_normalization.`nested_stream_with_complex_columns_resulting_into_long_names_partition_double_array_data`
  partition by timestamp_trunc(_airbyte_emitted_at, day)
  cluster by _airbyte_emitted_at
  OPTIONS()
  as (
    
-- Final base SQL model
select
    _airbyte_partition_hashid,
    id,
    _airbyte_ab_id,
    _airbyte_emitted_at,
    CURRENT_TIMESTAMP() as _airbyte_normalized_at,
    _airbyte_double_array_data_hashid
from `dataline-integration-testing`._airbyte_test_normalization.`nested_stream_with_complex_columns_resulting_into_long_names_partition_double_array_data_ab3`
-- double_array_data at nested_stream_with_complex_columns_resulting_into_long_names/partition/double_array_data from `dataline-integration-testing`.test_normalization.`nested_stream_with_complex_columns_resulting_into_long_names_partition`
where 1 = 1
  );
    