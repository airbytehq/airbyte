

  create or replace view `dataline-integration-testing`._airbyte_test_normalization.`nested_stream_with_complex_columns_resulting_into_long_names_partition_ab2`
  OPTIONS()
  as 
-- SQL model to cast each column to its adequate SQL type converted from the JSON schema type
select
    _airbyte_nested_stream_with_complex_columns_resulting_into_long_names_hashid,
    double_array_data,
    DATA,
    column___with__quotes,
    _airbyte_ab_id,
    _airbyte_emitted_at,
    CURRENT_TIMESTAMP() as _airbyte_normalized_at
from `dataline-integration-testing`._airbyte_test_normalization.`nested_stream_with_complex_columns_resulting_into_long_names_partition_ab1`
-- partition at nested_stream_with_complex_columns_resulting_into_long_names/partition
where 1 = 1;

