{{ config(
    cluster_by = ["_AIRBYTE_EMITTED_AT"],
    unique_key = env_var('AIRBYTE_DEFAULT_UNIQUE_KEY', '_AIRBYTE_AB_ID'),
    schema = "_AIRBYTE_TEST_NORMALIZATION",
    tags = [ "nested-intermediate" ]
) }}
-- SQL model to build a hash column based on the values of this record
select
    {{ dbt_utils.surrogate_key([
        '_AIRBYTE_CHILDREN_HASHID',
        'OWNER_ID',
    ]) }} as _AIRBYTE_OWNER_HASHID,
    tmp.*
from {{ ref('UNNEST_ALIAS_CHILDREN_OWNER_AB2') }} tmp
-- OWNER at unnest_alias/children/owner
where 1 = 1

