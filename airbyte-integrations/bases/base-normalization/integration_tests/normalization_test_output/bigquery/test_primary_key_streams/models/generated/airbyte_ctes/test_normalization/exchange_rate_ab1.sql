{{ config(schema="_airbyte_test_normalization", tags=["top-level-intermediate"]) }}
-- SQL model to parse JSON blob stored in a single column and extract into separated field columns as described by the JSON Schema
select
    {{ json_extract_scalar('_airbyte_data', ['id'], ['id']) }} as id,
    {{ json_extract_scalar('_airbyte_data', ['currency'], ['currency']) }} as currency,
    {{ json_extract_scalar('_airbyte_data', ['date'], ['date']) }} as date,
    {{ json_extract_scalar('_airbyte_data', ['HKD@spéçiäl & characters'], ['HKD@spéçiäl & characters']) }} as HKD_special___characters,
    {{ json_extract_scalar('_airbyte_data', ['HKD_special___characters'], ['HKD_special___characters']) }} as HKD_special___characters_1,
    {{ json_extract_scalar('_airbyte_data', ['NZD'], ['NZD']) }} as NZD,
    {{ json_extract_scalar('_airbyte_data', ['USD'], ['USD']) }} as USD,
    _airbyte_emitted_at
from {{ source('test_normalization', '_airbyte_raw_exchange_rate') }}
-- exchange_rate

