{{ config(
    indexes = [{'columns':['_airbyte_emitted_at'],'type':'btree'}],
    schema = "_airbyte_test_normalization",
    tags = [ "nested-intermediate" ]
) }}
-- SQL model to build a hash column based on the values of this record
-- depends_on: {{ ref('unnest_alias_childre__column___with__quotes_ab2') }}
select
    {{ dbt_utils.surrogate_key([
        '_airbyte_owner_hashid',
        'currency',
    ]) }} as _airbyte_column___with__quotes_hashid,
    tmp.*
from {{ ref('unnest_alias_childre__column___with__quotes_ab2') }} tmp
-- column___with__quotes at unnest_alias/children/owner/column`_'with"_quotes
where 1 = 1

