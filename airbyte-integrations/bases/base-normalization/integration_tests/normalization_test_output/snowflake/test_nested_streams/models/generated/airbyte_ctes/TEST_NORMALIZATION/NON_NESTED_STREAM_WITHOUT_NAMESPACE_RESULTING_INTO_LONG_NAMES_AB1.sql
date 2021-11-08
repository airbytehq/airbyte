{{ config(
    cluster_by = ["_AIRBYTE_EMITTED_AT"],
    unique_key = env_var('AIRBYTE_DEFAULT_UNIQUE_KEY', '_AIRBYTE_AB_ID'),
    schema = "_AIRBYTE_TEST_NORMALIZATION",
    tags = [ "top-level-intermediate" ]
) }}
-- SQL model to parse JSON blob stored in a single column and extract into separated field columns as described by the JSON Schema
select
    {{ json_extract_scalar('_airbyte_data', ['id'], ['id']) }} as ID,
    {{ json_extract_scalar('_airbyte_data', ['date'], ['date']) }} as DATE,
    _AIRBYTE_AB_ID,
    _AIRBYTE_EMITTED_AT,
    {{ current_timestamp() }} as _AIRBYTE_NORMALIZED_AT
from {{ source('TEST_NORMALIZATION', '_AIRBYTE_RAW_NON_NESTED_STREAM_WITHOUT_NAMESPACE_RESULTING_INTO_LONG_NAMES') }} as table_alias
-- NON_NESTED_STREAM_WITHOUT_NAMESPACE_RESULTING_INTO_LONG_NAMES
where 1 = 1

