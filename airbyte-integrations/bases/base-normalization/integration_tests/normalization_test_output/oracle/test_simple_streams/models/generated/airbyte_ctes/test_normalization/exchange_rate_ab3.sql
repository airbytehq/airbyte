{{ config(
    unique_key = env_var('AIRBYTE_DEFAULT_UNIQUE_KEY', quote('_AIRBYTE_AB_ID')),
    schema = "test_normalization",
    tags = [ "top-level-intermediate" ]
) }}
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
    ]) }} as {{ quote('_AIRBYTE_EXCHANGE_RATE_HASHID') }},
    tmp.*
from {{ ref('exchange_rate_ab2') }} tmp
-- exchange_rate
where 1 = 1
{{ incremental_clause(quote('_AIRBYTE_EMITTED_AT')) }}

