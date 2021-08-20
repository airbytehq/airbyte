{{ config(schema="SYSTEM", tags=["top-level"]) }}
-- Final base SQL model
select
    ID,
    NAME,
    {{ QUOTE('_AB_CDC_LSN') }},
    {{ QUOTE('_AB_CDC_UPDATED_AT') }},
    {{ QUOTE('_AB_CDC_DELETED_AT') }},
    airbyte_emitted_at,
    AIRBYTE_DEDUP_CDC_EXCLUDED_HASHID
from {{ ref('DEDUP_CDC_EXCLUDED_SCD') }}
-- DEDUP_CDC_EXCLUDED from {{ source('SYSTEM', 'AIRBYTE_RAW_DEDUP_CDC_EXCLUDED') }}
where airbyte_active_row = 'Latest'

