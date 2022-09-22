{{ config(
    indexes = [{'columns':['_airbyte_emitted_at'],'type':'btree'}],
    unique_key = '_airbyte_ab_id',
    schema = "_airbyte_test_normalization",
    tags = [ "top-level-intermediate" ]
) }}
-- SQL model to parse JSON blob stored in a single column and extract into separated field columns as described by the JSON Schema
-- depends_on: {{ source('test_normalization', '_airbyte_raw_arrays') }}
select
    {{ json_extract_string_array('_airbyte_data', ['array_of_strings'], ['array_of_strings']) }} as array_of_strings,
    {{ json_extract('table_alias', '_airbyte_data', ['nested_array_parent'], ['nested_array_parent']) }} as nested_array_parent,
    _airbyte_ab_id,
    _airbyte_emitted_at,
    {{ current_timestamp() }} as _airbyte_normalized_at
from {{ source('test_normalization', '_airbyte_raw_arrays') }} as table_alias
-- arrays
where 1 = 1

