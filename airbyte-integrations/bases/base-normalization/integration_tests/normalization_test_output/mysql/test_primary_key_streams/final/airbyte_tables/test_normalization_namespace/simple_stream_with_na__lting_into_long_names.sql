

  create  table
    test_normalization_namespace.`simple_stream_with_na__lting_into_long_names__dbt_tmp`
  as (
    
-- Final base SQL model
select
    id,
    `date`,
    _airbyte_emitted_at,
    _airbyte_simple_strea__nto_long_names_hashid
from _airbyte_test_normalization_namespace.`simple_stream_with_na__g_into_long_names_ab3`
-- simple_stream_with_na__lting_into_long_names from test_normalization_namespace._airbyte_raw_simple_s__lting_into_long_names
  )
