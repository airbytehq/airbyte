{{ config(
    unique_key = quote('_AIRBYTE_AB_ID'),
    schema = "test_normalization",
    tags = [ "top-level-intermediate" ]
) }}
-- SQL model to build a hash column based on the values of this record
-- depends_on: {{ ref('dedup_exchange_rate_ab2') }}
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
where 1 = 1
{{ incremental_clause(quote('_AIRBYTE_EMITTED_AT'), this) }}

