{{ config(
    indexes = [{'columns':['_airbyte_emitted_at'],'type':'btree'}],
    unique_key = '_airbyte_ab_id',
    schema = "_airbyte_test_normalization_namespace",
    tags = [ "top-level-intermediate" ]
) }}
-- SQL model to parse JSON blob stored in a single column and extract into separated field columns as described by the JSON Schema
-- depends_on: {{ source('test_normalization_namespace', '_airbyte_raw_simple_stream_with_namespace_resulting_into_long_names') }}
select
    {{ json_extract_scalar('_airbyte_data', ['id'], ['id']) }} as {{ adapter.quote('id') }},
    {{ json_extract_scalar('_airbyte_data', ['date'], ['date']) }} as {{ adapter.quote('date') }},
    _airbyte_ab_id,
    _airbyte_emitted_at,
    {{ current_timestamp() }} as _airbyte_normalized_at
from {{ source('test_normalization_namespace', '_airbyte_raw_simple_stream_with_namespace_resulting_into_long_names') }} as table_alias
-- simple_stream_with_n__lting_into_long_names
where 1 = 1
{{ incremental_clause('_airbyte_emitted_at', this) }}

