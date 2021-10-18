

  create or replace view `dataline-integration-testing`._airbyte_test_normalization.`nested_stream_with_complex_columns_resulting_into_long_names_partition_double_array_data_ab2`
  OPTIONS()
  as 
-- SQL model to cast each column to its adequate SQL type converted from the JSON schema type
select
    _airbyte_partition_hashid,
    cast(id as 
    string
) as id,
    _airbyte_emitted_at
from `dataline-integration-testing`._airbyte_test_normalization.`nested_stream_with_complex_columns_resulting_into_long_names_partition_double_array_data_ab1`
-- double_array_data at nested_stream_with_complex_columns_resulting_into_long_names/partition/double_array_data;

