{{ config(schema="_AIRBYTE_TEST_NORMALIZATION_NAMESPACE", tags=["top-level-intermediate"]) }}
-- SQL model to parse JSON blob stored in a single column and extract into separated field columns as described by the JSON Schema
select
    {{ json_extract_scalar('_airbyte_data', ['id'], ['id']) }} as ID,
    {{ json_extract_scalar('_airbyte_data', ['date'], ['date']) }} as DATE,
    _airbyte_emitted_at
from {{ source('TEST_NORMALIZATION_NAMESPACE', '_AIRBYTE_RAW_SIMPLE_STREAM_WITH_NAMESPACE_RESULTING_INTO_LONG_NAMES') }} as table_alias
-- SIMPLE_STREAM_WITH_NAMESPACE_RESULTING_INTO_LONG_NAMES

