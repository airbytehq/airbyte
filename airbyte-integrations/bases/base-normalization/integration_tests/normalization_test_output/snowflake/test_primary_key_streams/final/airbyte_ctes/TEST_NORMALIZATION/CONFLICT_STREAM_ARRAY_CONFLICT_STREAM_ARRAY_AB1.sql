
  create or replace  view "AIRBYTE_DATABASE"._AIRBYTE_TEST_NORMALIZATION."CONFLICT_STREAM_ARRAY_CONFLICT_STREAM_ARRAY_AB1"  as (
    
-- SQL model to parse JSON blob stored in a single column and extract into separated field columns as described by the JSON Schema
select
    _AIRBYTE_CONFLICT_STREAM_ARRAY_HASHID,
    get_path(parse_json(CONFLICT_STREAM_ARRAY), '"conflict_stream_name"') as CONFLICT_STREAM_NAME,
    _airbyte_emitted_at
from "AIRBYTE_DATABASE".TEST_NORMALIZATION."CONFLICT_STREAM_ARRAY" as table_alias
where CONFLICT_STREAM_ARRAY is not null
-- CONFLICT_STREAM_ARRAY at conflict_stream_array/conflict_stream_array
  );
