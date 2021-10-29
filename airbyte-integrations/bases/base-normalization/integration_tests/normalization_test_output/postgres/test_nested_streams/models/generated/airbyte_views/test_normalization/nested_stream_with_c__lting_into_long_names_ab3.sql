{{ config(
    indexes = [{'columns':['_airbyte_emitted_at'],'type':'hash'}],
    unique_key = env_var('AIRBYTE_DEFAULT_UNIQUE_KEY', '_airbyte_ab_id'),
    schema = "_airbyte_test_normalization",
    tags = [ "top-level-intermediate" ]
) }}
-- SQL model to build a hash column based on the values of this record
select
    {{ dbt_utils.surrogate_key([
        adapter.quote('id'),
        adapter.quote('date'),
        adapter.quote('partition'),
    ]) }} as _airbyte_nested_stre__nto_long_names_hashid,
    tmp.*
from {{ ref('nested_stream_with_c__lting_into_long_names_ab2') }} tmp
-- nested_stream_with_c__lting_into_long_names
where 1 = 1
{{ incremental_clause('_airbyte_emitted_at') }}

