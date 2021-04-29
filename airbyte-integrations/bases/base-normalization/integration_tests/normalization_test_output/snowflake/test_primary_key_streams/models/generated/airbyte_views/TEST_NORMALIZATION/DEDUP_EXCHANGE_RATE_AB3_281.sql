{{ config(alias="DEDUP_EXCHANGE_RATE_AB3", schema="_AIRBYTE_TEST_NORMALIZATION", tags=["top-level-intermediate"]) }}
-- SQL model to build a hash column based on the values of this record
select
    *,
    {{ dbt_utils.surrogate_key([
        'ID',
        'CURRENCY',
        'DATE',
        adapter.quote('HKD@spéçiäl & characters'),
        'NZD',
        'USD',
    ]) }} as _AIRBYTE_DEDUP_EXCHANGE_RATE_HASHID
from {{ ref('DEDUP_EXCHANGE_RATE_AB2_281') }}
-- DEDUP_EXCHANGE_RATE

