{{ config(
    unique_key = "{{ quote('_AIRBYTE_UNIQUE_KEY') }}",
    schema = "test_normalization",
    tags = [ "top-level" ]
) }}
-- Final base SQL model
-- depends_on: {{ ref('dedup_exchange_rate_scd') }}
select
    {{ quote('_AIRBYTE_UNIQUE_KEY') }},
    id,
    currency,
    {{ quote('DATE') }},
    timestamp_col,
    hkd_special___characters,
    hkd_special___characters_1,
    nzd,
    usd,
    {{ quote('_AIRBYTE_AB_ID') }},
    {{ quote('_AIRBYTE_EMITTED_AT') }},
    {{ current_timestamp() }} as {{ quote('_AIRBYTE_NORMALIZED_AT') }},
    {{ quote('_AIRBYTE_DEDUP_EXCHANGE_RATE_HASHID') }}
from {{ ref('dedup_exchange_rate_scd') }}
-- dedup_exchange_rate from {{ source('test_normalization', 'airbyte_raw_dedup_exchange_rate') }}
where 1 = 1
and {{ quote('_AIRBYTE_ACTIVE_ROW') }} = 1
{{ incremental_clause(quote('_AIRBYTE_EMITTED_AT'), this) }}

