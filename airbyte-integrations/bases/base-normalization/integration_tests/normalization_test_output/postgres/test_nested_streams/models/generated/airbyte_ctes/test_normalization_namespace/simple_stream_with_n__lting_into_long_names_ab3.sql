{{ config(
    indexes = [{'columns':['_airbyte_emitted_at'],'type':'hash'}],
    unique_key = env_var('AIRBYTE_DEFAULT_UNIQUE_KEY', '_airbyte_ab_id'),
    schema = "_airbyte_test_normalization_namespace",
    tags = [ "top-level-intermediate" ]
) }}
-- SQL model to build a hash column based on the values of this record
select
    {{ dbt_utils.surrogate_key([
        adapter.quote('id'),
        adapter.quote('date'),
    ]) }} as _airbyte_simple_stre__nto_long_names_hashid,
    tmp.*
from {{ ref('simple_stream_with_n__lting_into_long_names_ab2') }} tmp
-- simple_stream_with_n__lting_into_long_names
where 1 = 1

