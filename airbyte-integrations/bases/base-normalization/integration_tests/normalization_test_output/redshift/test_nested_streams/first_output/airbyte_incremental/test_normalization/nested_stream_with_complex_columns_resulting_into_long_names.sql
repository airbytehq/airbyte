
      

  create  table
    "integrationtests".test_normalization_xjvlg."nested_stream_with_complex_columns_resulting_into_long_names"
    
    
      compound sortkey(_airbyte_unique_key,_airbyte_emitted_at)
    
  as (
    
-- Final base SQL model
-- depends_on: "integrationtests".test_normalization_xjvlg."nested_stream_with_complex_columns_resulting_into_long_names_scd"
select
    _airbyte_unique_key,
    id,
    date,
    "partition",
    _airbyte_ab_id,
    _airbyte_emitted_at,
    getdate() as _airbyte_normalized_at,
    _airbyte_nested_stream_with_complex_columns_resulting_into_long_names_hashid
from "integrationtests".test_normalization_xjvlg."nested_stream_with_complex_columns_resulting_into_long_names_scd"
-- nested_stream_with_complex_columns_resulting_into_long_names from "integrationtests".test_normalization_xjvlg._airbyte_raw_nested_stream_with_complex_columns_resulting_into_long_names
where 1 = 1
and _airbyte_active_row = 1

  );
  