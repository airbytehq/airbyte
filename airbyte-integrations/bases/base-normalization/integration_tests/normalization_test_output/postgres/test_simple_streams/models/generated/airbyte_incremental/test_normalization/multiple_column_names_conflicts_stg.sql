{{ config(
    indexes = [{'columns':['_airbyte_emitted_at'],'type':'btree'}],
    unique_key = '_airbyte_ab_id',
    schema = "_airbyte_test_normalization",
    tags = [ "top-level-intermediate" ]
) }}
-- SQL model to build a hash column based on the values of this record
-- depends_on: {{ ref('multiple_column_names_conflicts_ab2') }}
select
    {{ dbt_utils.surrogate_key([
        adapter.quote('id'),
        adapter.quote('User Id'),
        'user_id',
        adapter.quote('User id'),
        adapter.quote('user id'),
        adapter.quote('User@Id'),
        'userid',
    ]) }} as _airbyte_multiple_co__ames_conflicts_hashid,
    tmp.*
from {{ ref('multiple_column_names_conflicts_ab2') }} tmp
-- multiple_column_names_conflicts
where 1 = 1
{{ incremental_clause('_airbyte_emitted_at', this) }}

