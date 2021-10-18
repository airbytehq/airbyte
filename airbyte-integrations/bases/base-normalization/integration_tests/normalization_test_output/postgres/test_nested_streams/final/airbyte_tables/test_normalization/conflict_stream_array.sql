

  create  table "postgres".test_normalization."conflict_stream_array__dbt_tmp"
  as (
    
-- Final base SQL model
select
    "id",
    conflict_stream_array,
    _airbyte_emitted_at,
    _airbyte_conflict_stream_array_hashid
from "postgres"._airbyte_test_normalization."conflict_stream_array_ab3"
-- conflict_stream_array from "postgres".test_normalization._airbyte_raw_conflict_stream_array
  );