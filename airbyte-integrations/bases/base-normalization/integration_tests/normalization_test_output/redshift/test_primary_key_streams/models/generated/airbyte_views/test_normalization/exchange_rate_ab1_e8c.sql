{{ config(alias="exchange_rate_ab1", schema="_airbyte_test_normalization", tags=["top-level-intermediate"]) }}
-- SQL model to parse JSON blob stored in a single column and extract into separated field columns as described by the JSON Schema
select
    {{ json_extract_scalar('_airbyte_data', ['id']) }} as id,
    {{ json_extract_scalar('_airbyte_data', ['currency']) }} as currency,
    {{ json_extract_scalar('_airbyte_data', ['date']) }} as date,
    {{ json_extract_scalar('_airbyte_data', ['HKD']) }} as hkd,
    {{ json_extract_scalar('_airbyte_data', ['NZD']) }} as nzd,
    {{ json_extract_scalar('_airbyte_data', ['USD']) }} as usd,
    _airbyte_emitted_at
from {{ source('test_normalization', '_airbyte_raw_exchange_rate') }}
-- exchange_rate

