{{ config(schema="test_normalization", tags=["top-level"]) }}
-- Final base SQL model
select
    {{ adapter.quote('id') }},
    {{ adapter.quote('name') }},
    _ab_cdc_lsn,
    _ab_cdc_updated_at,
    _ab_cdc_deleted_at,
    _ab_cdc_log_pos,
    _airbyte_emitted_at,
    _airbyte_pos_dedup_cdcx_hashid
from {{ ref('pos_dedup_cdcx_scd') }}
-- pos_dedup_cdcx from {{ source('test_normalization', '_airbyte_raw_pos_dedup_cdcx') }}
where _airbyte_active_row = 1

