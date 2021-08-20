
  create view SYSTEM.CONFLICT_STREAM_SCALAR_AB1__dbt_tmp as
    
-- SQL model to parse JSON blob stored in a single column and extract into separated field columns as described by the JSON Schema
select
    json_value(airbyte_data, '$."id"') as ID,
    json_value(airbyte_data, '$."conflict_stream_scalar"') as CONFLICT_STREAM_SCALAR,
    airbyte_emitted_at
from "SYSTEM"."AIRBYTE_RAW_CONFLICT_STREAM_SCALAR"
-- CONFLICT_STREAM_SCALAR

