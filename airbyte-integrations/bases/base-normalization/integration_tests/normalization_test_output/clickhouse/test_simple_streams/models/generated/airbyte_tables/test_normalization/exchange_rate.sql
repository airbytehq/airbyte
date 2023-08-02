{{ config(
    unique_key = '_airbyte_ab_id',
    schema = "test_normalization",
    tags = [ "top-level" ]
) }}
-- Final base SQL model
-- depends_on: {{ ref('exchange_rate_ab3') }}
select
    id,
    currency,
    date,
    timestamp_col,
    {{ quote('HKD@spéçiäl & characters') }},
    HKD_special___characters,
    NZD,
    USD,
    {{ quote('column___with__quotes') }},
    datetime_tz,
    datetime_no_tz,
    time_tz,
    time_no_tz,
    _airbyte_ab_id,
    _airbyte_emitted_at,
    {{ current_timestamp() }} as _airbyte_normalized_at,
    _airbyte_exchange_rate_hashid
from {{ ref('exchange_rate_ab3') }}
-- exchange_rate from {{ source('test_normalization', '_airbyte_raw_exchange_rate') }}
where 1 = 1

