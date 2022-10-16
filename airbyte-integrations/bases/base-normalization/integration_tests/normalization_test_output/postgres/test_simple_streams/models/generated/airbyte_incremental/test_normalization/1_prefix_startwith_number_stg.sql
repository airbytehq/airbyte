{{ config(
    indexes = [{'columns':['_airbyte_emitted_at'],'type':'btree'}],
    unique_key = '_airbyte_ab_id',
    schema = "_airbyte_test_normalization",
    tags = [ "top-level-intermediate" ]
) }}
-- SQL model to build a hash column based on the values of this record
-- depends_on: {{ ref('1_prefix_startwith_number_ab2') }}
select
    {{ dbt_utils.surrogate_key([
        adapter.quote('id'),
        adapter.quote('date'),
        adapter.quote('text'),
    ]) }} as _airbyte_1_prefix_startwith_number_hashid,
    tmp.*
from {{ ref('1_prefix_startwith_number_ab2') }} tmp
-- 1_prefix_startwith_number
where 1 = 1
{{ incremental_clause('_airbyte_emitted_at', this) }}

