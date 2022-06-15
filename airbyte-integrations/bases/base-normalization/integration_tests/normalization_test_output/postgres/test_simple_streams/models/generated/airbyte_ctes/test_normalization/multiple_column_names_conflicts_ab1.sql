{{ config(
    indexes = [{'columns':['_airbyte_emitted_at'],'type':'btree'}],
    unique_key = '_airbyte_ab_id',
    schema = "_airbyte_test_normalization",
    tags = [ "top-level-intermediate" ]
) }}
-- SQL model to parse JSON blob stored in a single column and extract into separated field columns as described by the JSON Schema
-- depends_on: {{ source('test_normalization', '_airbyte_raw_multiple_column_names_conflicts') }}
select
    {{ json_extract_scalar('_airbyte_data', ['id'], ['id']) }} as {{ adapter.quote('id') }},
    {{ json_extract_scalar('_airbyte_data', ['User Id'], ['User Id']) }} as {{ adapter.quote('User Id') }},
    {{ json_extract_scalar('_airbyte_data', ['user_id'], ['user_id']) }} as user_id,
    {{ json_extract_scalar('_airbyte_data', ['User id'], ['User id']) }} as {{ adapter.quote('User id') }},
    {{ json_extract_scalar('_airbyte_data', ['user id'], ['user id']) }} as {{ adapter.quote('user id') }},
    {{ json_extract_scalar('_airbyte_data', ['User@Id'], ['User@Id']) }} as {{ adapter.quote('User@Id') }},
    {{ json_extract_scalar('_airbyte_data', ['UserId'], ['UserId']) }} as userid,
    _airbyte_ab_id,
    _airbyte_emitted_at,
    {{ current_timestamp() }} as _airbyte_normalized_at
from {{ source('test_normalization', '_airbyte_raw_multiple_column_names_conflicts') }} as table_alias
-- multiple_column_names_conflicts
where 1 = 1
{{ incremental_clause('_airbyte_emitted_at', this) }}

