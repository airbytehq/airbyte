

  create or replace view `dataline-integration-testing`._airbyte_test_normalization.`non_nested_stream_without_namespace_resulting_into_long_names_ab1`
  OPTIONS()
  as 
-- SQL model to parse JSON blob stored in a single column and extract into separated field columns as described by the JSON Schema
select
    json_extract_scalar(_airbyte_data, "$['id']") as id,
    json_extract_scalar(_airbyte_data, "$['date']") as date,
    _airbyte_emitted_at
from `dataline-integration-testing`.test_normalization._airbyte_raw_non_nested_stream_without_namespace_resulting_into_long_names as table_alias
-- non_nested_stream_without_namespace_resulting_into_long_names;

