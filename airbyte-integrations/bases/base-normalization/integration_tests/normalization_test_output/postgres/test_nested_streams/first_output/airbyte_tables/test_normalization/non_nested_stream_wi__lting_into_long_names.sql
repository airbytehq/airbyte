

  create  table "postgres".test_normalization."non_nested_stream_wi__lting_into_long_names__dbt_tmp"
  as (
    
-- Final base SQL model
select
    "id",
    "date",
    _airbyte_ab_id,
    _airbyte_emitted_at,
    now() as _airbyte_normalized_at,
    _airbyte_non_nested___nto_long_names_hashid
from "postgres"._airbyte_test_normalization."non_nested_stream_wi__lting_into_long_names_ab3"
-- non_nested_stream_wi__lting_into_long_names from "postgres".test_normalization._airbyte_raw_non_nested_stream_without_namespace_resulting_into_long_names
where 1 = 1
  );