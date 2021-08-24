{{ config(schema="test_normalization", tags=["top-level-intermediate"]) }}
-- SQL model to parse JSON blob stored in a single column and extract into separated field columns as described by the JSON Schema
select
    {{ json_extract_scalar('airbyte_data', ['id'], ['id']) }} as id,
    {{ json_extract_scalar('airbyte_data', ['name'], ['name']) }} as name,
    {{ json_extract_scalar('airbyte_data', ['_ab_cdc_lsn'], ['_ab_cdc_lsn']) }} as {{ QUOTE('_AB_CDC_LSN') }},
    {{ json_extract_scalar('airbyte_data', ['_ab_cdc_updated_at'], ['_ab_cdc_updated_at']) }} as {{ QUOTE('_AB_CDC_UPDATED_AT') }},
    {{ json_extract_scalar('airbyte_data', ['_ab_cdc_deleted_at'], ['_ab_cdc_deleted_at']) }} as {{ QUOTE('_AB_CDC_DELETED_AT') }},
    airbyte_emitted_at
from {{ source('test_normalization', 'airbyte_raw_dedup_cdc_excluded') }} 
-- dedup_cdc_excluded

