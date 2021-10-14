{{ config(schema="TEST_NORMALIZATION", tags=["top-level"]) }}
-- Final base SQL model
select
    ID,
    NAME,
    _AB_CDC_LSN,
    _AB_CDC_UPDATED_AT,
    _AB_CDC_DELETED_AT,
    _AB_CDC_LOG_POS,
    _AIRBYTE_EMITTED_AT,
    _AIRBYTE_POS_DEDUP_CDCX_HASHID
from {{ ref('POS_DEDUP_CDCX_SCD') }}
-- POS_DEDUP_CDCX from {{ source('TEST_NORMALIZATION', '_AIRBYTE_RAW_POS_DEDUP_CDCX') }}
where _airbyte_active_row = 1

