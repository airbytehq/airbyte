{{ config(
    unique_key = env_var('AIRBYTE_DEFAULT_UNIQUE_KEY', '_airbyte_ab_id'),
    schema = "_airbyte_test_normalization",
    tags = [ "top-level-intermediate" ]
) }}
-- SQL model to build a hash column based on the values of this record
select
    {{ dbt_utils.surrogate_key([
        'id',
        array_to_string('children'),
    ]) }} as _airbyte_unnest_alias_hashid,
    tmp.*
from {{ ref('unnest_alias_ab2') }} tmp
-- unnest_alias
where 1 = 1
{{ incremental_clause('_airbyte_emitted_at') }}

