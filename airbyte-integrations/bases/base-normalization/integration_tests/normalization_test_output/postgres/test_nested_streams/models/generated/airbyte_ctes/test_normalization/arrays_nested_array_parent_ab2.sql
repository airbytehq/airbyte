{{ config(
    indexes = [{'columns':['_airbyte_emitted_at'],'type':'btree'}],
    schema = "_airbyte_test_normalization",
    tags = [ "nested-intermediate" ]
) }}
-- SQL model to cast each column to its adequate SQL type converted from the JSON schema type
-- depends_on: {{ ref('arrays_nested_array_parent_ab1') }}
select
    _airbyte_arrays_hashid,
    nested_array,
    _airbyte_ab_id,
    _airbyte_emitted_at,
    {{ current_timestamp() }} as _airbyte_normalized_at
from {{ ref('arrays_nested_array_parent_ab1') }}
-- nested_array_parent at arrays/nested_array_parent
where 1 = 1

