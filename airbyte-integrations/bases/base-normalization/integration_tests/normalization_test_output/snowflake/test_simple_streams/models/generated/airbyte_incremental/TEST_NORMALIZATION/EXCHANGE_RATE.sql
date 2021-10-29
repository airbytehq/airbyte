{{ config(
    cluster_by = ["_AIRBYTE_EMITTED_AT"],
    unique_key = env_var('AIRBYTE_DEFAULT_UNIQUE_KEY', '_AIRBYTE_AB_ID'),
    schema = "TEST_NORMALIZATION",
    tags = [ "top-level" ]
) }}
-- Final base SQL model
select
    ID,
    CURRENCY,
    DATE,
    TIMESTAMP_COL,
    {{ adapter.quote('HKD@spéçiäl & characters') }},
    HKD_SPECIAL___CHARACTERS,
    NZD,
    USD,
    _AIRBYTE_AB_ID,
    _AIRBYTE_EMITTED_AT,
    {{ current_timestamp() }} as _AIRBYTE_NORMALIZED_AT,
    _AIRBYTE_EXCHANGE_RATE_HASHID
from {{ ref('EXCHANGE_RATE_AB3') }}
-- EXCHANGE_RATE from {{ source('TEST_NORMALIZATION', '_AIRBYTE_RAW_EXCHANGE_RATE') }}
where 1 = 1
{{ incremental_clause('_AIRBYTE_EMITTED_AT') }}

