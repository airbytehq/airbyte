{{ config(schema="test_normalization", tags=["top-level"]) }}
-- Final base SQL model
select
    id,
    name,
    {{ QUOTE('_AB_CDC_LSN') }},
    {{ QUOTE('_AB_CDC_UPDATED_AT') }},
    {{ QUOTE('_AB_CDC_DELETED_AT') }},
    airbyte_emitted_at,
    {{ QUOTE('_AIRBYTE_DEDUP_CDC_EXCLUDED_HASHID') }}
from {{ ref('dedup_cdc_excluded_scd') }}
-- dedup_cdc_excluded from {{ source('test_normalization', 'airbyte_raw_dedup_cdc_excluded') }}
where airbyte_active_row = 'Latest'

