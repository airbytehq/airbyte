
  create view SYSTEM.EXCHANGE_RATE_AB1__dbt_tmp as
    
-- SQL model to parse JSON blob stored in a single column and extract into separated field columns as described by the JSON Schema
select
    json_value(airbyte_data, '$."id"') as ID,
    json_value(airbyte_data, '$."currency"') as CURRENCY,
    json_value(airbyte_data, '$."date"') as "DATE",
    json_value(airbyte_data, '$."timestamp_col"') as TIMESTAMP_COL,
    json_value(airbyte_data, '$."HKD@spéçiäl & characters"') as HKD_SPECIAL___CHARACTERS,
    json_value(airbyte_data, '$."HKD_special___characters"') as HKD_SPECIAL___CHARACTERS_1,
    json_value(airbyte_data, '$."NZD"') as NZD,
    json_value(airbyte_data, '$."USD"') as USD,
    airbyte_emitted_at
from "SYSTEM"."AIRBYTE_RAW_EXCHANGE_RATE"
-- EXCHANGE_RATE

