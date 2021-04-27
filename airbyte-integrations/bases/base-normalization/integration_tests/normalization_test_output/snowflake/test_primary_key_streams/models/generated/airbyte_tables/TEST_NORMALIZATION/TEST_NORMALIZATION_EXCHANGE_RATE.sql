{{ config(alias="EXCHANGE_RATE", schema="TEST_NORMALIZATION", tags=["top-level"]) }}
-- Final base SQL model
select
    ID,
    CURRENCY,
    DATE,
    HKD,
    NZD,
    USD,
    _airbyte_emitted_at,
    _AIRBYTE_EXCHANGE_RATE_HASHID
from {{ ref('_AIRBYTE_TEST_NORMALIZATION_EXCHANGE_RATE_AB3') }}
-- EXCHANGE_RATE from {{ source('TEST_NORMALIZATION', '_AIRBYTE_RAW_EXCHANGE_RATE') }}

