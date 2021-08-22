{{ config(schema="TEST_NORMALIZATION", tags=["top-level"]) }}
-- Final base SQL model
select
    ID,
    NAME,
    {{ QUOTE('_AB_CDC_LSN') }},
    {{ QUOTE('_AB_CDC_UPDATED_AT') }},
    {{ QUOTE('_AB_CDC_DELETED_AT') }},
    airbyte_emitted_at,
    {{ QUOTE('_AIRBYTE_DEDUP_CDC_EXCLUDED_HASHID') }}
from {{ ref('DEDUP_CDC_EXCLUDED_SCD') }}
-- DEDUP_CDC_EXCLUDED from {{ source('TEST_NORMALIZATION', 'AIRBYTE_RAW_DEDUP_CDC_EXCLUDED') }}
where airbyte_active_row = 'Latest'

