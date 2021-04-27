{{ config(alias="DEDUP_EXCHANGE_RATE_AB3", schema="_AIRBYTE_TEST_NORMALIZATION", tags=["top-level-intermediate"]) }}
-- SQL model to build a hash column based on the values of this record
select
    *,
    {{ dbt_utils.surrogate_key([
        'ID',
        'CURRENCY',
        'DATE',
        'HKD',
        'NZD',
        'USD',
    ]) }} as _AIRBYTE_DEDUP_EXCHANGE_RATE_HASHID
from {{ ref('_AIRBYTE_TEST_NORMALIZATION_DEDUP_EXCHANGE_RATE_AB2') }}
-- DEDUP_EXCHANGE_RATE

