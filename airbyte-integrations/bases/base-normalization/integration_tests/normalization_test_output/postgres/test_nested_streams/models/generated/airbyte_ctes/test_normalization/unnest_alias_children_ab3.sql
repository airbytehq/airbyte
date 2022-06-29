{{ config(
    indexes = [{'columns':['_airbyte_emitted_at'],'type':'btree'}],
    schema = "_airbyte_test_normalization",
    tags = [ "nested-intermediate" ]
) }}
-- SQL model to build a hash column based on the values of this record
-- depends_on: {{ ref('unnest_alias_children_ab2') }}
select
    {{ dbt_utils.surrogate_key([
        '_airbyte_unnest_alias_hashid',
        'ab_id',
        object_to_string(adapter.quote('owner')),
    ]) }} as _airbyte_children_hashid,
    tmp.*
from {{ ref('unnest_alias_children_ab2') }} tmp
-- children at unnest_alias/children
where 1 = 1

