{{ config(
    indexes = [{'columns':['_airbyte_emitted_at'],'type':'btree'}],
    schema = "_airbyte_test_normalization",
    tags = [ "nested-intermediate" ]
) }}
-- SQL model to parse JSON blob stored in a single column and extract into separated field columns as described by the JSON Schema
-- depends_on: {{ ref('arrays') }}
select
    _airbyte_arrays_hashid,
    {{ json_extract_string_array('nested_array_parent', ['nested_array'], ['nested_array']) }} as nested_array,
    _airbyte_ab_id,
    _airbyte_emitted_at,
    {{ current_timestamp() }} as _airbyte_normalized_at
from {{ ref('arrays') }} as table_alias
-- nested_array_parent at arrays/nested_array_parent
where 1 = 1
and nested_array_parent is not null

