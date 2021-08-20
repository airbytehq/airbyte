
  create view SYSTEM.NON_NESTED_STREAM_WITHOUT_NAMESPACE_RESULTING_INTO_LONG_NAMES_AB1__dbt_tmp as
    
-- SQL model to parse JSON blob stored in a single column and extract into separated field columns as described by the JSON Schema
select
    json_value(airbyte_data, '$."id"') as ID,
    json_value(airbyte_data, '$."date"') as "DATE",
    airbyte_emitted_at
from "SYSTEM"."AIRBYTE_RAW_NON_NESTED_STREAM_WITHOUT_NAMESPACE_RESULTING_INTO_LONG_NAMES"
-- NON_NESTED_STREAM_WITHOUT_NAMESPACE_RESULTING_INTO_LONG_NAMES

