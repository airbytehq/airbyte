{{ config(schema="_airbyte_test_normalization", tags=["top-level-intermediate"]) }}
-- SQL model to build a hash column based on the values of this record
select
    *,
    {{ dbt_utils.surrogate_key([
        'id',
        'currency',
        'date',
        'timestamp_col',
        adapter.quote('hkd@spéçiäl & characters'),
        'hkd_special___characters',
        'nzd',
        'usd',
    ]) }} as _airbyte_dedup_exchange_rate_hashid
from {{ ref('dedup_exchange_rate_ab2') }}
-- dedup_exchange_rate

