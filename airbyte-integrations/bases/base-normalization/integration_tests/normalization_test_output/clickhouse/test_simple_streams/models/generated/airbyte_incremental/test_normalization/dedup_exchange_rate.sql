{{ config(
    unique_key = "_airbyte_unique_key",
    schema = "test_normalization",
    tags = [ "top-level" ]
) }}
-- Final base SQL model
-- depends_on: {{ ref('dedup_exchange_rate_scd') }}
select
    _airbyte_unique_key,
    id,
    currency,
    date,
    timestamp_col,
    {{ quote('HKD@spéçiäl & characters') }},
    HKD_special___characters,
    NZD,
    USD,
    _airbyte_ab_id,
    _airbyte_emitted_at,
    {{ current_timestamp() }} as _airbyte_normalized_at,
    _airbyte_dedup_exchange_rate_hashid
from {{ ref('dedup_exchange_rate_scd') }}
-- dedup_exchange_rate from {{ source('test_normalization', '_airbyte_raw_dedup_exchange_rate') }}
where 1 = 1
and _airbyte_active_row = 1
{{ incremental_clause('_airbyte_emitted_at', this) }}

