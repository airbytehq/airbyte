

  create  table "postgres".test_normalization."nested_stream_with_complex_co_64a_partition_44f__dbt_tmp"
  as (
    
-- Final base SQL model
select
    _airbyte_nested_stre__nto_long_names_hashid,
    double_array_data,
    "DATA",
    _airbyte_emitted_at,
    _airbyte_partition_hashid
from "postgres"._airbyte_test_normalization."nested_stream_with_comple_64a_partition_ab3"
-- partition at nested_stream_with_complex_columns_resulting_into_long_names/partition from "postgres".test_normalization."nested_stream_with_c__lting_into_long_names"
  );