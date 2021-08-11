

  create  table "postgres".test_normalization."conflict_stream_array_conflict_stream_array__dbt_tmp"
  as (
    
-- Final base SQL model
select
    _airbyte_conflict_stream_array_hashid,
    conflict_stream_name,
    _airbyte_emitted_at,
    _airbyte_conflict_stream_array_2_hashid
from "postgres"._airbyte_test_normalization."conflict_stream_array_conflict_stream_array_ab3"
-- conflict_stream_array at conflict_stream_array/conflict_stream_array from "postgres".test_normalization."conflict_stream_array"
  );