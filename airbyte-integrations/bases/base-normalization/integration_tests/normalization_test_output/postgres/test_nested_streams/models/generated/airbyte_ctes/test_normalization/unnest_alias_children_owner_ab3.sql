{{ config(
    indexes = [{'columns':['_airbyte_emitted_at'],'type':'btree'}],
    schema = "_airbyte_test_normalization",
    tags = [ "nested-intermediate" ]
) }}
-- SQL model to build a hash column based on the values of this record
-- depends_on: {{ ref('unnest_alias_children_owner_ab2') }}
select
    {{ dbt_utils.surrogate_key([
        '_airbyte_children_hashid',
        'owner_id',
        array_to_string(adapter.quote('column`_\'with""_quotes')),
    ]) }} as _airbyte_owner_hashid,
    tmp.*
from {{ ref('unnest_alias_children_owner_ab2') }} tmp
-- owner at unnest_alias/children/owner
where 1 = 1

