
  create view SYSTEM.NESTED_STREAM_WITH_COMPLEX_COLUMNS_RESULTING_INTO_LONG_NAMES_AB1__dbt_tmp as
    
-- SQL model to parse JSON blob stored in a single column and extract into separated field columns as described by the JSON Schema
select
    json_value(airbyte_data, '$."id"') as ID,
    json_value(airbyte_data, '$."date"') as "DATE",
    json_value(airbyte_data, '$."partition"') as PARTITION,
    airbyte_emitted_at
from "SYSTEM"."AIRBYTE_RAW_NESTED_STREAM_WITH_COMPLEX_COLUMNS_RESULTING_INTO_LONG_NAMES"
-- NESTED_STREAM_WITH_COMPLEX_COLUMNS_RESULTING_INTO_LONG_NAMES

