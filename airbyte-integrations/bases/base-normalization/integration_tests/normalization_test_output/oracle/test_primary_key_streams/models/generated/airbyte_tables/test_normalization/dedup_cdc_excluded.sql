{{ config(schema="test_normalization", tags=["top-level"]) }}
-- Final base SQL model
select
    id,
    name,
    {{ quote('_AB_CDC_LSN') }},
    {{ quote('_AB_CDC_UPDATED_AT') }},
    {{ quote('_AB_CDC_DELETED_AT') }},
    {{ quote('_AIRBYTE_EMITTED_AT') }},
    {{ quote('_AIRBYTE_DEDUP_CDC_EXCLUDED_HASHID') }}
from {{ ref('dedup_cdc_excluded_scd') }}
-- dedup_cdc_excluded from {{ source('test_normalization', 'airbyte_raw_dedup_cdc_excluded') }}
where "_AIRBYTE_ACTIVE_ROW" = 1

