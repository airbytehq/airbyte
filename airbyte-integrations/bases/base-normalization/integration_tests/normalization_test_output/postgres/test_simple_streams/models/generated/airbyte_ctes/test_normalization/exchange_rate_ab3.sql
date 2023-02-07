{{ config(
    indexes = [{'columns':['_airbyte_emitted_at'],'type':'btree'}],
    unique_key = '_airbyte_ab_id',
    schema = "_airbyte_test_normalization",
    tags = [ "top-level-intermediate" ]
) }}
-- SQL model to build a hash column based on the values of this record
-- depends_on: {{ ref('exchange_rate_ab2') }}
select
    {{ dbt_utils.surrogate_key([
        adapter.quote('id'),
        'currency',
        adapter.quote('date'),
        'timestamp_col',
        adapter.quote('HKD@spéçiäl & characters'),
        'hkd_special___characters',
        'nzd',
        'usd',
        adapter.quote('column`_\'with""_quotes'),
        'datetime_tz',
        'datetime_no_tz',
        'time_tz',
        'time_no_tz',
        'property_binary_data',
    ]) }} as _airbyte_exchange_rate_hashid,
    tmp.*
from {{ ref('exchange_rate_ab2') }} tmp
-- exchange_rate
where 1 = 1

