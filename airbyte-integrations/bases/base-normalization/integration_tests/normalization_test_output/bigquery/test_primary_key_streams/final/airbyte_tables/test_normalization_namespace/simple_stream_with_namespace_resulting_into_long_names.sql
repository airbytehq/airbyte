

  create or replace table `dataline-integration-testing`.test_normalization_namespace.`simple_stream_with_namespace_resulting_into_long_names`
  
  
  OPTIONS()
  as (
    
-- Final base SQL model
select
    id,
    date,
    _airbyte_emitted_at,
    _airbyte_simple_stream_with_namespace_resulting_into_long_names_hashid
from `dataline-integration-testing`._airbyte_test_normalization_namespace.`simple_stream_with_namespace_resulting_into_long_names_ab3`
-- simple_stream_with_namespace_resulting_into_long_names from `dataline-integration-testing`.test_normalization_namespace._airbyte_raw_simple_stream_with_namespace_resulting_into_long_names
  );
    