{{ config(schema="test_normalization", tags=["top-level-intermediate"]) }}
-- SQL model to build a hash column based on the values of this record
select
    {{ dbt_utils.surrogate_key([
        'id',
        'currency',
        quote('DATE'),
        'timestamp_col',
        'hkd_special___characters',
        'hkd_special___characters_1',
        'nzd',
        'usd',
    ]) }} as {{ quote('_AIRBYTE_DEDUP_EXCHANGE_RATE_HASHID') }},
    tmp.*
from {{ ref('dedup_exchange_rate_ab2') }} tmp
-- dedup_exchange_rate

