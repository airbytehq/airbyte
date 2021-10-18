

  create or replace table `dataline-integration-testing`.test_normalization.`non_nested_stream_without_namespace_resulting_into_long_names`
  
  
  OPTIONS()
  as (
    
-- Final base SQL model
select
    id,
    date,
    _airbyte_emitted_at,
    _airbyte_non_nested_stream_without_namespace_resulting_into_long_names_hashid
from `dataline-integration-testing`._airbyte_test_normalization.`non_nested_stream_without_namespace_resulting_into_long_names_ab3`
-- non_nested_stream_without_namespace_resulting_into_long_names from `dataline-integration-testing`.test_normalization._airbyte_raw_non_nested_stream_without_namespace_resulting_into_long_names
  );
    