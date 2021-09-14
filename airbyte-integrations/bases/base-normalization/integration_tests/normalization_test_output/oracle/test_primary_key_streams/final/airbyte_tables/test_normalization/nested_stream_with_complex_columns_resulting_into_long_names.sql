

  create  table test_normalization.nested_stream_with_complex_columns_resulting_into_long_names__dbt_tmp
  
  as
    
-- Final base SQL model
select
    id,
    "DATE",
    partition,
    "_AIRBYTE_EMITTED_AT",
    "_AIRBYTE_NESTED_STREAM_WITH_COMPLEX_COLUMNS_RESULTING_INTO_LONG_NAMES_HASHID"
from test_normalization.nested_stream_with_complex_columns_resulting_into_long_names_scd
-- nested_stream_with_complex_columns_resulting_into_long_names from test_normalization.airbyte_raw_nested_stream_with_complex_columns_resulting_into_long_names
where "_AIRBYTE_ACTIVE_ROW" = 1