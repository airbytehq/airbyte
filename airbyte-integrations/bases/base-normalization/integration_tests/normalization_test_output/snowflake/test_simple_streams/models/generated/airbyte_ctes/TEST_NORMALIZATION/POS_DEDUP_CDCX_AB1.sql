{{ config(schema="_AIRBYTE_TEST_NORMALIZATION", tags=["top-level-intermediate"]) }}
-- SQL model to parse JSON blob stored in a single column and extract into separated field columns as described by the JSON Schema
select
    {{ json_extract_scalar('_airbyte_data', ['id'], ['id']) }} as ID,
    {{ json_extract_scalar('_airbyte_data', ['name'], ['name']) }} as NAME,
    {{ json_extract_scalar('_airbyte_data', ['_ab_cdc_lsn'], ['_ab_cdc_lsn']) }} as _AB_CDC_LSN,
    {{ json_extract_scalar('_airbyte_data', ['_ab_cdc_updated_at'], ['_ab_cdc_updated_at']) }} as _AB_CDC_UPDATED_AT,
    {{ json_extract_scalar('_airbyte_data', ['_ab_cdc_deleted_at'], ['_ab_cdc_deleted_at']) }} as _AB_CDC_DELETED_AT,
    {{ json_extract_scalar('_airbyte_data', ['_ab_cdc_log_pos'], ['_ab_cdc_log_pos']) }} as _AB_CDC_LOG_POS,
    _AIRBYTE_EMITTED_AT
from {{ source('TEST_NORMALIZATION', '_AIRBYTE_RAW_POS_DEDUP_CDCX') }} as table_alias
-- POS_DEDUP_CDCX

