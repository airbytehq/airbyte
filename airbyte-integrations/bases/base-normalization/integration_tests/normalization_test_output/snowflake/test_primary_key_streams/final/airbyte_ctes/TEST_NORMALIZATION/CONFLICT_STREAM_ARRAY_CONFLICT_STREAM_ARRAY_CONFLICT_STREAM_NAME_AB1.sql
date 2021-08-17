
  create or replace  view "AIRBYTE_DATABASE"._AIRBYTE_TEST_NORMALIZATION."CONFLICT_STREAM_ARRAY_CONFLICT_STREAM_ARRAY_CONFLICT_STREAM_NAME_AB1"  as (
    
-- SQL model to parse JSON blob stored in a single column and extract into separated field columns as described by the JSON Schema

select
    _AIRBYTE_CONFLICT_STREAM_ARRAY_2_HASHID,
    to_varchar(get_path(parse_json(CONFLICT_STREAM_NAME.value), '"id"')) as ID,
    _airbyte_emitted_at
from "AIRBYTE_DATABASE".TEST_NORMALIZATION."CONFLICT_STREAM_ARRAY_CONFLICT_STREAM_ARRAY" as table_alias
cross join table(flatten(CONFLICT_STREAM_NAME)) as CONFLICT_STREAM_NAME
where CONFLICT_STREAM_NAME is not null
-- CONFLICT_STREAM_NAME at conflict_stream_array/conflict_stream_array/conflict_stream_name
  );
