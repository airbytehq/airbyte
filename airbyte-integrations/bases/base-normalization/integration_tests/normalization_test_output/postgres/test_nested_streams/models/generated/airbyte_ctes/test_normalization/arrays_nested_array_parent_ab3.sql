{{ config(
    indexes = [{'columns':['_airbyte_emitted_at'],'type':'btree'}],
    schema = "_airbyte_test_normalization",
    tags = [ "nested-intermediate" ]
) }}
-- SQL model to build a hash column based on the values of this record
-- depends_on: {{ ref('arrays_nested_array_parent_ab2') }}
select
    {{ dbt_utils.surrogate_key([
        '_airbyte_arrays_hashid',
        array_to_string('nested_array'),
    ]) }} as _airbyte_nested_array_parent_hashid,
    tmp.*
from {{ ref('arrays_nested_array_parent_ab2') }} tmp
-- nested_array_parent at arrays/nested_array_parent
where 1 = 1

