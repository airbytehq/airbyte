{{ config(
    cluster_by = ["_AIRBYTE_EMITTED_AT"],
    unique_key = env_var('AIRBYTE_DEFAULT_UNIQUE_KEY', '_AIRBYTE_AB_ID'),
    schema = "_AIRBYTE_TEST_NORMALIZATION",
    tags = [ "nested-intermediate" ]
) }}
-- SQL model to parse JSON blob stored in a single column and extract into separated field columns as described by the JSON Schema
select
    _AIRBYTE_CONFLICT_STREAM_NAME_2_HASHID,
    {{ json_extract_scalar('CONFLICT_STREAM_NAME', ['groups'], ['groups']) }} as GROUPS,
    _AIRBYTE_AB_ID,
    _AIRBYTE_EMITTED_AT,
    {{ current_timestamp() }} as _AIRBYTE_NORMALIZED_AT
from {{ ref('CONFLICT_STREAM_NAME_CONFLICT_STREAM_NAME') }} as table_alias
-- CONFLICT_STREAM_NAME at conflict_stream_name/conflict_stream_name/conflict_stream_name
where 1 = 1
and CONFLICT_STREAM_NAME is not null

