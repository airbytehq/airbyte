

  create  table
    "integrationtests".test_normalization."nested_stream_with_complex_columns_resulting_into_long_names__dbt_tmp"
    
    
  as (
    
-- Final base SQL model
select
    id,
    date,
    "partition",
    _airbyte_emitted_at,
    _airbyte_nested_stream_with_complex_columns_resulting_into_long_names_hashid
from "integrationtests".test_normalization."nested_stream_with_complex_columns_resulting_into_long_names_scd"
-- nested_stream_with_complex_columns_resulting_into_long_names from "integrationtests".test_normalization._airbyte_raw_nested_stream_with_complex_columns_resulting_into_long_names
where _airbyte_active_row = True
  );