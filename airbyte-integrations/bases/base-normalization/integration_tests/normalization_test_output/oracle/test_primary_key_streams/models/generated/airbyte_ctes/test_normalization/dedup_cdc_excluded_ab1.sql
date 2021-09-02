{{ config(schema="test_normalization", tags=["top-level-intermediate"]) }}
-- SQL model to parse JSON blob stored in a single column and extract into separated field columns as described by the JSON Schema
select
    {{ json_extract_scalar(quote('_AIRBYTE_DATA'), ['id'], ['id']) }} as id,
    {{ json_extract_scalar(quote('_AIRBYTE_DATA'), ['name'], ['name']) }} as name,
    {{ json_extract_scalar(quote('_AIRBYTE_DATA'), ['_ab_cdc_lsn'], ['_ab_cdc_lsn']) }} as {{ quote('_AB_CDC_LSN') }},
    {{ json_extract_scalar(quote('_AIRBYTE_DATA'), ['_ab_cdc_updated_at'], ['_ab_cdc_updated_at']) }} as {{ quote('_AB_CDC_UPDATED_AT') }},
    {{ json_extract_scalar(quote('_AIRBYTE_DATA'), ['_ab_cdc_deleted_at'], ['_ab_cdc_deleted_at']) }} as {{ quote('_AB_CDC_DELETED_AT') }},
    {{ quote('_AIRBYTE_EMITTED_AT') }}
from {{ source('test_normalization', 'airbyte_raw_dedup_cdc_excluded') }} 
-- dedup_cdc_excluded

