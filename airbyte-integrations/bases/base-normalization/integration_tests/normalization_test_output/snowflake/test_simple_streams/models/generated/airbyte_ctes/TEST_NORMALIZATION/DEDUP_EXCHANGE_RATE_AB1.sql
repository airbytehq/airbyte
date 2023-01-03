{{ config(
    cluster_by = ["_AIRBYTE_EMITTED_AT"],
    unique_key = '_AIRBYTE_AB_ID',
    schema = "_AIRBYTE_TEST_NORMALIZATION",
    tags = [ "top-level-intermediate" ]
) }}
-- SQL model to parse JSON blob stored in a single column and extract into separated field columns as described by the JSON Schema
-- depends_on: {{ source('TEST_NORMALIZATION', '_AIRBYTE_RAW_DEDUP_EXCHANGE_RATE') }}
select
    {{ json_extract_scalar('_airbyte_data', ['id'], ['id']) }} as ID,
    {{ json_extract_scalar('_airbyte_data', ['currency'], ['currency']) }} as CURRENCY,
    {{ json_extract_scalar('_airbyte_data', ['date'], ['date']) }} as DATE,
    {{ json_extract_scalar('_airbyte_data', ['timestamp_col'], ['timestamp_col']) }} as TIMESTAMP_COL,
    {{ json_extract_scalar('_airbyte_data', ['HKD@spéçiäl & characters'], ['HKD@spéçiäl & characters']) }} as {{ adapter.quote('HKD@spéçiäl & characters') }},
    {{ json_extract_scalar('_airbyte_data', ['HKD_special___characters'], ['HKD_special___characters']) }} as HKD_SPECIAL___CHARACTERS,
    {{ json_extract_scalar('_airbyte_data', ['NZD'], ['NZD']) }} as NZD,
    {{ json_extract_scalar('_airbyte_data', ['USD'], ['USD']) }} as USD,
    _AIRBYTE_AB_ID,
    _AIRBYTE_EMITTED_AT,
    {{ current_timestamp() }} as _AIRBYTE_NORMALIZED_AT
from {{ source('TEST_NORMALIZATION', '_AIRBYTE_RAW_DEDUP_EXCHANGE_RATE') }} as table_alias
-- DEDUP_EXCHANGE_RATE
where 1 = 1
{{ incremental_clause('_AIRBYTE_EMITTED_AT', this) }}

