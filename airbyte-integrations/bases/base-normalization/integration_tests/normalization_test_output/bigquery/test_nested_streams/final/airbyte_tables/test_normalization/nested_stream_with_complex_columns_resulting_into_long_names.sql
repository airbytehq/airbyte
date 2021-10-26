

  create or replace table `dataline-integration-testing`.test_normalization.`nested_stream_with_complex_columns_resulting_into_long_names`
  
  
  OPTIONS()
  as (
    
-- Final base SQL model
select
    id,
    date,
    `partition`,
    _airbyte_emitted_at,
    _airbyte_nested_stream_with_complex_columns_resulting_into_long_names_hashid
from `dataline-integration-testing`.test_normalization.`nested_stream_with_complex_columns_resulting_into_long_names_scd`
-- nested_stream_with_complex_columns_resulting_into_long_names from `dataline-integration-testing`.test_normalization._airbyte_raw_nested_stream_with_complex_columns_resulting_into_long_names
where _airbyte_active_row = 1
  );
    