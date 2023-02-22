{{ config(
    indexes = [{'columns':['_airbyte_emitted_at'],'type':'btree'}],
    unique_key = '_airbyte_ab_id',
    schema = "_airbyte_test_normalization",
    tags = [ "top-level-intermediate" ]
) }}
-- SQL model to build a hash column based on the values of this record
-- depends_on: {{ ref('types_testing_ab2') }}
select
    {{ dbt_utils.surrogate_key([
        adapter.quote('id'),
        'airbyte_integer_column',
        'nullable_airbyte_integer_column',
    ]) }} as _airbyte_types_testing_hashid,
    tmp.*
from {{ ref('types_testing_ab2') }} tmp
-- types_testing
where 1 = 1
{{ incremental_clause('_airbyte_emitted_at', this) }}

