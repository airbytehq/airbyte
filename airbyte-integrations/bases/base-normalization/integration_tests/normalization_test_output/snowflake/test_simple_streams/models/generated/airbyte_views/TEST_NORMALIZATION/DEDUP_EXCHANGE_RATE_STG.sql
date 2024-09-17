{{ config(
    cluster_by = ["_AIRBYTE_EMITTED_AT"],
    unique_key = '_AIRBYTE_AB_ID',
    schema = "_AIRBYTE_TEST_NORMALIZATION",
    tags = [ "top-level-intermediate" ]
) }}
-- SQL model to build a hash column based on the values of this record
-- depends_on: {{ ref('DEDUP_EXCHANGE_RATE_AB2') }}
select
    {{ dbt_utils.surrogate_key([
        'ID',
        'CURRENCY',
        'DATE',
        'TIMESTAMP_COL',
        adapter.quote('HKD@spéçiäl & characters'),
        'HKD_SPECIAL___CHARACTERS',
        'NZD',
        'USD',
    ]) }} as _AIRBYTE_DEDUP_EXCHANGE_RATE_HASHID,
    tmp.*
from {{ ref('DEDUP_EXCHANGE_RATE_AB2') }} tmp
-- DEDUP_EXCHANGE_RATE
where 1 = 1
{{ incremental_clause('_AIRBYTE_EMITTED_AT', this) }}

