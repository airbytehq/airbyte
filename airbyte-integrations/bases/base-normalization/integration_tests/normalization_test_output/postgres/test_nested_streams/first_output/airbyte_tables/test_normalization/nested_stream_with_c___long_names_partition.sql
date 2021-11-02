

  create  table "postgres".test_normalization."nested_stream_with_c___long_names_partition__dbt_tmp"
  as (
    
-- Final base SQL model
select
    _airbyte_nested_stre__nto_long_names_hashid,
    double_array_data,
    "DATA",
    "column`_'with""_quotes",
    _airbyte_ab_id,
    _airbyte_emitted_at,
    now() as _airbyte_normalized_at,
    _airbyte_partition_hashid
from "postgres"._airbyte_test_normalization."nested_stream_with_c___long_names_partition_ab3"
-- partition at nested_stream_with_complex_columns_resulting_into_long_names/partition from "postgres".test_normalization."nested_stream_with_c__lting_into_long_names"
where 1 = 1
  );