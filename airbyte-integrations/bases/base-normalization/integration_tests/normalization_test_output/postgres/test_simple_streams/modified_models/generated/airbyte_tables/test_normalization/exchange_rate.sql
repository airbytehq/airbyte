{{ config(
    indexes = [{'columns':['_airbyte_emitted_at'],'type':'btree'}],
    unique_key = '_airbyte_ab_id',
    schema = "test_normalization",
    tags = [ "top-level" ]
) }}
-- Final base SQL model
-- depends_on: {{ ref('exchange_rate_ab3') }}
select
    {{ adapter.quote('id') }},
    currency,
    new_column,
    {{ adapter.quote('date') }},
    timestamp_col,
    {{ adapter.quote('HKD@spéçiäl & characters') }},
    nzd,
    usd,
    {{ adapter.quote('column`_\'with""_quotes') }},
    _airbyte_ab_id,
    _airbyte_emitted_at,
    {{ current_timestamp() }} as _airbyte_normalized_at,
    _airbyte_exchange_rate_hashid
from {{ ref('exchange_rate_ab3') }}
-- exchange_rate from {{ source('test_normalization', '_airbyte_raw_exchange_rate') }}
where 1 = 1

