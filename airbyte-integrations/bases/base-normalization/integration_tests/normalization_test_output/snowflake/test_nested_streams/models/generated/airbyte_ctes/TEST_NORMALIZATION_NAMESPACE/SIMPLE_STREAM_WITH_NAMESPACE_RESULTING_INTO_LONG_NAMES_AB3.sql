{{ config(
    cluster_by = ["_AIRBYTE_EMITTED_AT"],
    unique_key = env_var('AIRBYTE_DEFAULT_UNIQUE_KEY', '_AIRBYTE_AB_ID'),
    schema = "_AIRBYTE_TEST_NORMALIZATION_NAMESPACE",
    tags = [ "top-level-intermediate" ]
) }}
-- SQL model to build a hash column based on the values of this record
select
    {{ dbt_utils.surrogate_key([
        'ID',
        'DATE',
    ]) }} as _AIRBYTE_SIMPLE_STREAM_WITH_NAMESPACE_RESULTING_INTO_LONG_NAMES_HASHID,
    tmp.*
from {{ ref('SIMPLE_STREAM_WITH_NAMESPACE_RESULTING_INTO_LONG_NAMES_AB2') }} tmp
-- SIMPLE_STREAM_WITH_NAMESPACE_RESULTING_INTO_LONG_NAMES
where 1 = 1

