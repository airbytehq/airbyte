{{ config(
    indexes = [{'columns':['_airbyte_emitted_at'],'type':'btree'}],
    unique_key = '_airbyte_ab_id',
    schema = "_airbyte_test_normalization",
    tags = [ "top-level-intermediate" ]
) }}
-- SQL model to parse JSON blob stored in a single column and extract into separated field columns as described by the JSON Schema
-- depends_on: {{ source('test_normalization', '_airbyte_raw_types_testing') }}
select
    {{ json_extract_scalar('_airbyte_data', ['id'], ['id']) }} as {{ adapter.quote('id') }},
    {{ json_extract_scalar('_airbyte_data', ['airbyte_integer'], ['airbyte_integer']) }} as airbyte_integer,
    {{ json_extract_scalar('_airbyte_data', ['nullable_airbyte_integer'], ['nullable_airbyte_integer']) }} as nullable_airbyte_integer,
    {{ json_extract_scalar('_airbyte_data', ['big_integer'], ['big_integer']) }} as big_integer,
    {{ json_extract_scalar('_airbyte_data', ['nullable_big_integer'], ['nullable_big_integer']) }} as nullable_big_integer,
    _airbyte_ab_id,
    _airbyte_emitted_at,
    {{ current_timestamp() }} as _airbyte_normalized_at
from {{ source('test_normalization', '_airbyte_raw_types_testing') }} as table_alias
-- types_testing
where 1 = 1
{{ incremental_clause('_airbyte_emitted_at', this) }}

