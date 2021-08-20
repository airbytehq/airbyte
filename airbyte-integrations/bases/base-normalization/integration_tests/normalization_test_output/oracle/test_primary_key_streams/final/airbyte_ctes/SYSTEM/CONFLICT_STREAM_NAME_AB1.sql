
  create view SYSTEM.CONFLICT_STREAM_NAME_AB1__dbt_tmp as
    
-- SQL model to parse JSON blob stored in a single column and extract into separated field columns as described by the JSON Schema
select
    json_value(airbyte_data, '$."id"') as ID,
    json_value(airbyte_data, '$."conflict_stream_name"') as CONFLICT_STREAM_NAME,
    airbyte_emitted_at
from "SYSTEM"."AIRBYTE_RAW_CONFLICT_STREAM_NAME"
-- CONFLICT_STREAM_NAME

