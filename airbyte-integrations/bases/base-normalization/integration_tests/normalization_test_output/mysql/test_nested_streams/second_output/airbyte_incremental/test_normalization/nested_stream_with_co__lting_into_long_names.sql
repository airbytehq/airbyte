

  create  table
    test_normalization.`nested_stream_with_co__lting_into_long_names__dbt_tmp`
  as (
    
-- Final base SQL model
-- depends_on: test_normalization.`nested_stream_with_co_1g_into_long_names_scd`
select
    _airbyte_unique_key,
    id,
    `date`,
    `partition`,
    _airbyte_ab_id,
    _airbyte_emitted_at,
    
    CURRENT_TIMESTAMP
 as _airbyte_normalized_at,
    _airbyte_nested_strea__nto_long_names_hashid
from test_normalization.`nested_stream_with_co_1g_into_long_names_scd`
-- nested_stream_with_co__lting_into_long_names from test_normalization._airbyte_raw_nested_s__lting_into_long_names
where 1 = 1
and _airbyte_active_row = 1

  )
