{{ config(schema="SYSTEM", tags=["top-level-intermediate"]) }}
-- SQL model to parse JSON blob stored in a single column and extract into separated field columns as described by the JSON Schema
select
    {{ json_extract_scalar('airbyte_data', ['id']) }} as ID,
    {{ json_extract_scalar('airbyte_data', ['currency']) }} as CURRENCY,
    {{ json_extract_scalar('airbyte_data', ['date']) }} as {{ QUOTE('DATE') }},
    {{ json_extract_scalar('airbyte_data', ['timestamp_col']) }} as TIMESTAMP_COL,
    {{ json_extract_scalar('airbyte_data', ['HKD@spéçiäl & characters']) }} as HKD_SPECIAL___CHARACTERS,
    {{ json_extract_scalar('airbyte_data', ['HKD_special___characters']) }} as HKD_SPECIAL___CHARACTERS_1,
    {{ json_extract_scalar('airbyte_data', ['NZD']) }} as NZD,
    {{ json_extract_scalar('airbyte_data', ['USD']) }} as USD,
    airbyte_emitted_at
from {{ source('SYSTEM', 'AIRBYTE_RAW_EXCHANGE_RATE') }}
-- EXCHANGE_RATE

