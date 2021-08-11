

  create or replace view `dataline-integration-testing`._airbyte_test_normalization.`conflict_stream_array_conflict_stream_array_conflict_stream_name_ab1`
  OPTIONS()
  as 
-- SQL model to parse JSON blob stored in a single column and extract into separated field columns as described by the JSON Schema

select
    _airbyte_conflict_stream_array_2_hashid,
    json_extract_scalar(conflict_stream_name, "$['id']") as id,
    _airbyte_emitted_at
from `dataline-integration-testing`.test_normalization.`conflict_stream_array_conflict_stream_array` as table_alias
cross join unnest(conflict_stream_name) as conflict_stream_name
where conflict_stream_name is not null
-- conflict_stream_name at conflict_stream_array/conflict_stream_array/conflict_stream_name;

