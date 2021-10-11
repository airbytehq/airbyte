{{ config(schema="TEST_NORMALIZATION", tags=["top-level"]) }}
-- Final base SQL model
select
    ID,
    NAME,
    _AB_CDC_LSN,
    _AB_CDC_UPDATED_AT,
    _AB_CDC_DELETED_AT,
    _AIRBYTE_EMITTED_AT,
    _AIRBYTE_DEDUP_CDC_EXCLUDED_HASHID
from {{ ref('DEDUP_CDC_EXCLUDED_SCD') }}
-- DEDUP_CDC_EXCLUDED from {{ source('TEST_NORMALIZATION', '_AIRBYTE_RAW_DEDUP_CDC_EXCLUDED') }}
where _airbyte_active_row = 1

