
      

  create  table "postgres".test_normalization."nested_stream_with_c__lting_into_long_names"
  as (
    
-- Final base SQL model
-- depends_on: "postgres".test_normalization."nested_stream_with_c__lting_into_long_names_scd"
select
    _airbyte_unique_key,
    "id",
    "date",
    "partition",
    _airbyte_ab_id,
    _airbyte_emitted_at,
    now() as _airbyte_normalized_at,
    _airbyte_nested_stre__nto_long_names_hashid
from "postgres".test_normalization."nested_stream_with_c__lting_into_long_names_scd"
-- nested_stream_with_c__lting_into_long_names from "postgres".test_normalization._airbyte_raw_nested_stream_with_complex_columns_resulting_into_long_names
where 1 = 1
and _airbyte_active_row = 1

  );
  