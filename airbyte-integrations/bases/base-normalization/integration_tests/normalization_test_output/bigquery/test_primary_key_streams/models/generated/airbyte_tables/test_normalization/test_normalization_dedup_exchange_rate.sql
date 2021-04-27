{{ config(alias="dedup_exchange_rate", schema="test_normalization", tags=["top-level"]) }}
-- Final base SQL model
select
    id,
    currency,
    date,
    HKD,
    NZD,
    USD,
    _airbyte_emitted_at,
    _airbyte_dedup_exchange_rate_hashid
from {{ ref('test_normalization_dedup_exchange_rate_scd') }}
-- dedup_exchange_rate from {{ source('test_normalization', '_airbyte_raw_dedup_exchange_rate') }}
where _airbyte_active_row = True

