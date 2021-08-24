{{ config(schema="test_normalization", tags=["top-level-intermediate"]) }}
-- SQL model to parse JSON blob stored in a single column and extract into separated field columns as described by the JSON Schema
select
    {{ json_extract_scalar('airbyte_data', ['id'], ['id']) }} as id,
    {{ json_extract_scalar('airbyte_data', ['currency'], ['currency']) }} as currency,
    {{ json_extract_scalar('airbyte_data', ['date'], ['date']) }} as {{ QUOTE('DATE') }},
    {{ json_extract_scalar('airbyte_data', ['timestamp_col'], ['timestamp_col']) }} as timestamp_col,
    {{ json_extract_scalar('airbyte_data', ['HKD@spéçiäl & characters'], ['HKD@spéçiäl & characters']) }} as hkd_special___characters,
    {{ json_extract_scalar('airbyte_data', ['HKD_special___characters'], ['HKD_special___characters']) }} as hkd_special___characters_1,
    {{ json_extract_scalar('airbyte_data', ['NZD'], ['NZD']) }} as nzd,
    {{ json_extract_scalar('airbyte_data', ['USD'], ['USD']) }} as usd,
    airbyte_emitted_at
from {{ source('test_normalization', 'airbyte_raw_dedup_exchange_rate') }} 
-- dedup_exchange_rate

