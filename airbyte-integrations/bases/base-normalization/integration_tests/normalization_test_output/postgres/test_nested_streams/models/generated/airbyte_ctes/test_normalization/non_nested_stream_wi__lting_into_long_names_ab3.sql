{{ config(
    indexes = [{'columns':['_airbyte_emitted_at'],'type':'btree'}],
    unique_key = '_airbyte_ab_id',
    schema = "_airbyte_test_normalization",
    tags = [ "top-level-intermediate" ]
) }}
-- SQL model to build a hash column based on the values of this record
-- depends_on: {{ ref('non_nested_stream_wi__lting_into_long_names_ab2') }}
select
    {{ dbt_utils.surrogate_key([
        adapter.quote('id'),
        adapter.quote('date'),
    ]) }} as _airbyte_non_nested___nto_long_names_hashid,
    tmp.*
from {{ ref('non_nested_stream_wi__lting_into_long_names_ab2') }} tmp
-- non_nested_stream_wi__lting_into_long_names
where 1 = 1

