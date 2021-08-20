{{ config(schema="SYSTEM", tags=["top-level-intermediate"]) }}
-- SQL model to parse JSON blob stored in a single column and extract into separated field columns as described by the JSON Schema
select
    {{ json_extract_scalar('airbyte_data', ['id']) }} as ID,
    {{ json_extract_scalar('airbyte_data', ['name']) }} as NAME,
    {{ json_extract_scalar('airbyte_data', ['_ab_cdc_lsn']) }} as {{ QUOTE('_AB_CDC_LSN') }},
    {{ json_extract_scalar('airbyte_data', ['_ab_cdc_updated_at']) }} as {{ QUOTE('_AB_CDC_UPDATED_AT') }},
    {{ json_extract_scalar('airbyte_data', ['_ab_cdc_deleted_at']) }} as {{ QUOTE('_AB_CDC_DELETED_AT') }},
    airbyte_emitted_at
from {{ source('SYSTEM', 'AIRBYTE_RAW_DEDUP_CDC_EXCLUDED') }}
-- DEDUP_CDC_EXCLUDED

