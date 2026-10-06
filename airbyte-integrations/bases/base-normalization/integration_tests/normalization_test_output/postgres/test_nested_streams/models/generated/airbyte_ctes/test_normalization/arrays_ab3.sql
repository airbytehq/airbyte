{{ config(
    indexes = [{'columns':['_airbyte_emitted_at'],'type':'btree'}],
    unique_key = '_airbyte_ab_id',
    schema = "_airbyte_test_normalization",
    tags = [ "top-level-intermediate" ]
) }}
-- SQL model to build a hash column based on the values of this record
-- depends_on: {{ ref('arrays_ab2') }}
select
    {{ dbt_utils.surrogate_key([
        array_to_string('array_of_strings'),
        object_to_string('nested_array_parent'),
    ]) }} as _airbyte_arrays_hashid,
    tmp.*
from {{ ref('arrays_ab2') }} tmp
-- arrays
where 1 = 1

