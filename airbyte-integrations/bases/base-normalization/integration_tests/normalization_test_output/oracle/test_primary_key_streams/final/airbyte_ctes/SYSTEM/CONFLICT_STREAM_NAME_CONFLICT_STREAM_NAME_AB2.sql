
  create view SYSTEM.CONFLICT_STREAM_NAME_CONFLICT_STREAM_NAME_AB2__dbt_tmp as
    
-- SQL model to cast each column to its adequate SQL type converted from the JSON schema type
select
    AIRBYTE_CONFLICT_STREAM_NAME_HASHID,
    cast(CONFLICT_STREAM_NAME as varchar2(3000)) as CONFLICT_STREAM_NAME,
    airbyte_emitted_at
from SYSTEM.CONFLICT_STREAM_NAME_CONFLICT_STREAM_NAME_AB1
-- CONFLICT_STREAM_NAME at conflict_stream_name/conflict_stream_name

