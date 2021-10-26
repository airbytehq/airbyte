

  create or replace view `dataline-integration-testing`._airbyte_test_normalization.`nested_stream_with_complex_columns_resulting_into_long_names_partition_ab1`
  OPTIONS()
  as 
-- SQL model to parse JSON blob stored in a single column and extract into separated field columns as described by the JSON Schema
select
    _airbyte_nested_stream_with_complex_columns_resulting_into_long_names_hashid,
    json_extract_array(`partition`, "$['double_array_data']") as double_array_data,
    json_extract_array(`partition`, "$['DATA']") as DATA,
    json_extract_array(`partition`, "$['column___with__quotes']") as column___with__quotes,
    _airbyte_emitted_at
from `dataline-integration-testing`.test_normalization.`nested_stream_with_complex_columns_resulting_into_long_names` as table_alias
where `partition` is not null
-- partition at nested_stream_with_complex_columns_resulting_into_long_names/partition;

