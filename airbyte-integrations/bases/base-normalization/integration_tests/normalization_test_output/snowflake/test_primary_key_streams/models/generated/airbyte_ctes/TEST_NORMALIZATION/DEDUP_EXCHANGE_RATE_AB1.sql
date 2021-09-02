{{ config(schema="_AIRBYTE_TEST_NORMALIZATION", tags=["top-level-intermediate"]) }}
-- SQL model to parse JSON blob stored in a single column and extract into separated field columns as described by the JSON Schema
select
    {{ json_extract_scalar('_airbyte_data', ['id'], ['id']) }} as ID,
    {{ json_extract_scalar('_airbyte_data', ['currency'], ['currency']) }} as CURRENCY,
    {{ json_extract_scalar('_airbyte_data', ['date'], ['date']) }} as DATE,
    {{ json_extract_scalar('_airbyte_data', ['timestamp_col'], ['timestamp_col']) }} as TIMESTAMP_COL,
    {{ json_extract_scalar('_airbyte_data', ['HKD@spéçiäl & characters'], ['HKD@spéçiäl & characters']) }} as {{ adapter.quote('HKD@spéçiäl & characters') }},
    {{ json_extract_scalar('_airbyte_data', ['HKD_special___characters'], ['HKD_special___characters']) }} as HKD_SPECIAL___CHARACTERS,
    {{ json_extract_scalar('_airbyte_data', ['NZD'], ['NZD']) }} as NZD,
    {{ json_extract_scalar('_airbyte_data', ['USD'], ['USD']) }} as USD,
    _airbyte_emitted_at
from {{ source('TEST_NORMALIZATION', '_AIRBYTE_RAW_DEDUP_EXCHANGE_RATE') }} as table_alias
-- DEDUP_EXCHANGE_RATE

