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
        'CONFLICT_STREAM_NAME',
    ]) }} as _AIRBYTE_CONFLICT_STREAM_NAME_HASHID,
    tmp.*
from {{ ref('CONFLICT_STREAM_NAME_AB2') }} tmp
-- CONFLICT_STREAM_NAME
where 1 = 1

