

  create or replace table `dataline-integration-testing`.test_normalization.`conflict_stream_array_conflict_stream_array`
  
  
  OPTIONS()
  as (
    
-- Final base SQL model
select
    _airbyte_conflict_stream_array_hashid,
    conflict_stream_name,
    _airbyte_emitted_at,
    _airbyte_conflict_stream_array_2_hashid
from `dataline-integration-testing`._airbyte_test_normalization.`conflict_stream_array_conflict_stream_array_ab3`
-- conflict_stream_array at conflict_stream_array/conflict_stream_array from `dataline-integration-testing`.test_normalization.`conflict_stream_array`
  );
    