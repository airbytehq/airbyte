{{ config(
    cluster_by = ["_AIRBYTE_EMITTED_AT"],
    unique_key = env_var('AIRBYTE_DEFAULT_UNIQUE_KEY', '_AIRBYTE_AB_ID'),
    schema = "_AIRBYTE_TEST_NORMALIZATION",
    tags = [ "nested-intermediate" ]
) }}
-- SQL model to cast each column to its adequate SQL type converted from the JSON schema type
select
    _AIRBYTE_CONFLICT_STREAM_NAME_2_HASHID,
    cast(GROUPS as {{ dbt_utils.type_string() }}) as GROUPS,
    _AIRBYTE_AB_ID,
    _AIRBYTE_EMITTED_AT,
    {{ current_timestamp() }} as _AIRBYTE_NORMALIZED_AT
from {{ ref('CONFLICT_STREAM_NAME_CONFLICT_STREAM_NAME_CONFLICT_STREAM_NAME_AB1') }}
-- CONFLICT_STREAM_NAME at conflict_stream_name/conflict_stream_name/conflict_stream_name
where 1 = 1

