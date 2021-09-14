{{ config(schema="test_normalization", tags=["top-level"]) }}
-- Final base SQL model
select
    id,
    name,
    _ab_cdc_lsn,
    _ab_cdc_updated_at,
    _ab_cdc_deleted_at,
    _airbyte_emitted_at,
    _airbyte_dedup_cdc_excluded_hashid
from {{ ref('dedup_cdc_excluded_scd') }}
-- dedup_cdc_excluded from {{ source('test_normalization', '_airbyte_raw_dedup_cdc_excluded') }}
where _airbyte_active_row = 1

