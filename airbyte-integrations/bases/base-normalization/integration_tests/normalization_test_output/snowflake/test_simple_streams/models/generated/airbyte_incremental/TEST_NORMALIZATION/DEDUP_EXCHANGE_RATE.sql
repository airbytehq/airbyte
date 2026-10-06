{{ config(
    cluster_by = ["_AIRBYTE_UNIQUE_KEY", "_AIRBYTE_EMITTED_AT"],
    unique_key = "_AIRBYTE_UNIQUE_KEY",
    schema = "TEST_NORMALIZATION",
    tags = [ "top-level" ]
) }}
-- Final base SQL model
-- depends_on: {{ ref('DEDUP_EXCHANGE_RATE_SCD') }}
select
    _AIRBYTE_UNIQUE_KEY,
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
    _AIRBYTE_DEDUP_EXCHANGE_RATE_HASHID
from {{ ref('DEDUP_EXCHANGE_RATE_SCD') }}
-- DEDUP_EXCHANGE_RATE from {{ source('TEST_NORMALIZATION', '_AIRBYTE_RAW_DEDUP_EXCHANGE_RATE') }}
where 1 = 1
and _AIRBYTE_ACTIVE_ROW = 1
{{ incremental_clause('_AIRBYTE_EMITTED_AT', this) }}

