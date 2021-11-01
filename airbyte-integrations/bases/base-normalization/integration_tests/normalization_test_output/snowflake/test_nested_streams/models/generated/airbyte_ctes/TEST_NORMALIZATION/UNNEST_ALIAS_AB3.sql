{{ config(
    cluster_by = ["_AIRBYTE_EMITTED_AT"],
    unique_key = env_var('AIRBYTE_DEFAULT_UNIQUE_KEY', '_AIRBYTE_AB_ID'),
    schema = "_AIRBYTE_TEST_NORMALIZATION",
    tags = [ "top-level-intermediate" ]
) }}
-- SQL model to build a hash column based on the values of this record
select
    {{ dbt_utils.surrogate_key([
        'ID',
        array_to_string('CHILDREN'),
    ]) }} as _AIRBYTE_UNNEST_ALIAS_HASHID,
    tmp.*
from {{ ref('UNNEST_ALIAS_AB2') }} tmp
-- UNNEST_ALIAS
where 1 = 1
{{ incremental_clause('_AIRBYTE_EMITTED_AT') }}

