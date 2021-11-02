{{ config(
    sort = "_airbyte_emitted_at",
    unique_key = env_var('AIRBYTE_DEFAULT_UNIQUE_KEY', '_airbyte_ab_id'),
    schema = "_airbyte_test_normalization",
    tags = [ "top-level-intermediate" ]
) }}
-- SQL model to build a hash column based on the values of this record
select
    {{ dbt_utils.surrogate_key([
        'id',
        'date',
    ]) }} as _airbyte_non_nested_stream_without_namespace_resulting_into_long_names_hashid,
    tmp.*
from {{ ref('non_nested_stream_without_namespace_resulting_into_long_names_ab2') }} tmp
-- non_nested_stream_without_namespace_resulting_into_long_names
where 1 = 1

