

  create  table "postgres".test_normalization_namespace."simple_stream_with_n__lting_into_long_names__dbt_tmp"
  as (
    
-- Final base SQL model
select
    "id",
    "date",
    _airbyte_ab_id,
    _airbyte_emitted_at,
    now() as _airbyte_normalized_at,
    _airbyte_simple_stre__nto_long_names_hashid
from "postgres"._airbyte_test_normalization_namespace."simple_stream_with_n__lting_into_long_names_ab3"
-- simple_stream_with_n__lting_into_long_names from "postgres".test_normalization_namespace._airbyte_raw_simple_stream_with_namespace_resulting_into_long_names
where 1 = 1
  );