
  create view SYSTEM.CONFLICT_STREAM_ARRAY_CONFLICT_STREAM_ARRAY_CONFLICT_STREAM_NAME_AB1__dbt_tmp as
    
-- SQL model to parse JSON blob stored in a single column and extract into separated field columns as described by the JSON Schema

select
    AIRBYTE_CONFLICT_STREAM_ARRAY_2_HASHID,
    json_value(CONFLICT_STREAM_NAME, '$."id"') as ID,
    airbyte_emitted_at
from SYSTEM.CONFLICT_STREAM_ARRAY_CONFLICT_STREAM_ARRAY

where CONFLICT_STREAM_NAME is not null
-- CONFLICT_STREAM_NAME at conflict_stream_array/conflict_stream_array/conflict_stream_name

