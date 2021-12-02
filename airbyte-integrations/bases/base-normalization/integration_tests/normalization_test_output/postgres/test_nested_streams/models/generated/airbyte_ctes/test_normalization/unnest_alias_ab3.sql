{{ config(
    indexes = [{'columns':['_airbyte_emitted_at'],'type':'btree'}],
    unique_key = '_airbyte_ab_id',
    schema = "_airbyte_test_normalization",
    tags = [ "top-level-intermediate" ]
) }}
-- SQL model to build a hash column based on the values of this record
-- depends_on: {{ ref('unnest_alias_ab2') }}
select
    {{ dbt_utils.surrogate_key([
        adapter.quote('id'),
        array_to_string('children'),
    ]) }} as _airbyte_unnest_alias_hashid,
    tmp.*
from {{ ref('unnest_alias_ab2') }} tmp
-- unnest_alias
where 1 = 1

