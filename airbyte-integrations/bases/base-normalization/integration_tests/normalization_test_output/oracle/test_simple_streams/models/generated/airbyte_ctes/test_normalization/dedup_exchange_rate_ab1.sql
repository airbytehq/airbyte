{{ config(
    unique_key = quote('_AIRBYTE_AB_ID'),
    schema = "test_normalization",
    tags = [ "top-level-intermediate" ]
) }}
-- SQL model to parse JSON blob stored in a single column and extract into separated field columns as described by the JSON Schema
-- depends_on: {{ source('test_normalization', 'airbyte_raw_dedup_exchange_rate') }}
select
    {{ json_extract_scalar(quote('_AIRBYTE_DATA'), ['id'], ['id']) }} as id,
    {{ json_extract_scalar(quote('_AIRBYTE_DATA'), ['currency'], ['currency']) }} as currency,
    {{ json_extract_scalar(quote('_AIRBYTE_DATA'), ['date'], ['date']) }} as {{ quote('DATE') }},
    {{ json_extract_scalar(quote('_AIRBYTE_DATA'), ['timestamp_col'], ['timestamp_col']) }} as timestamp_col,
    {{ json_extract_scalar(quote('_AIRBYTE_DATA'), ['HKD@spéçiäl & characters'], ['HKD@spéçiäl & characters']) }} as hkd_special___characters,
    {{ json_extract_scalar(quote('_AIRBYTE_DATA'), ['HKD_special___characters'], ['HKD_special___characters']) }} as hkd_special___characters_1,
    {{ json_extract_scalar(quote('_AIRBYTE_DATA'), ['NZD'], ['NZD']) }} as nzd,
    {{ json_extract_scalar(quote('_AIRBYTE_DATA'), ['USD'], ['USD']) }} as usd,
    {{ quote('_AIRBYTE_AB_ID') }},
    {{ quote('_AIRBYTE_EMITTED_AT') }},
    {{ current_timestamp() }} as {{ quote('_AIRBYTE_NORMALIZED_AT') }}
from {{ source('test_normalization', 'airbyte_raw_dedup_exchange_rate') }} 
-- dedup_exchange_rate
where 1 = 1
{{ incremental_clause(quote('_AIRBYTE_EMITTED_AT'), this) }}

