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
        'DATE',
    ]) }} as _AIRBYTE_NON_NESTED_STREAM_WITHOUT_NAMESPACE_RESULTING_INTO_LONG_NAMES_HASHID,
    tmp.*
from {{ ref('NON_NESTED_STREAM_WITHOUT_NAMESPACE_RESULTING_INTO_LONG_NAMES_AB2') }} tmp
-- NON_NESTED_STREAM_WITHOUT_NAMESPACE_RESULTING_INTO_LONG_NAMES
where 1 = 1

