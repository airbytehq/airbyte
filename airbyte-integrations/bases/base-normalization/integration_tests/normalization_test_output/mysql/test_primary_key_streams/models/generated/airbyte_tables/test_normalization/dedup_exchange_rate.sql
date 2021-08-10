{{ config(schema="test_normalization", tags=["top-level"]) }}
-- Final base SQL model
select
    id,
    currency,
    {{ adapter.quote('date') }},
    timestamp_col,
    {{ adapter.quote('HKD@spéçiäl & characters') }},
    hkd_special___characters,
    nzd,
    usd,
    _airbyte_emitted_at,
    _airbyte_dedup_exchange_rate_hashid
from {{ ref('dedup_exchange_rate_scd') }}
-- dedup_exchange_rate from {{ source('test_normalization', '_airbyte_raw_dedup_exchange_rate') }}
where _airbyte_active_row = True

