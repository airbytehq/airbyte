

  create or replace view `dataline-integration-testing`._airbyte_test_normalization.`nested_stream_with_complex_columns_resulting_into_long_names_partition_double_array_data_ab1`
  OPTIONS()
  as 
-- SQL model to parse JSON blob stored in a single column and extract into separated field columns as described by the JSON Schema

select
    _airbyte_partition_hashid,
    json_extract_scalar(double_array_data, "$['id']") as id,
    _airbyte_emitted_at
from `dataline-integration-testing`.test_normalization.`nested_stream_with_complex_columns_resulting_into_long_names_partition` as table_alias
cross join unnest(double_array_data) as double_array_data
where double_array_data is not null
-- double_array_data at nested_stream_with_complex_columns_resulting_into_long_names/partition/double_array_data;

