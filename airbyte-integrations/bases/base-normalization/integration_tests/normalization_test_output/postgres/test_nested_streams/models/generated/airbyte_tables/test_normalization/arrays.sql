{{ config(
    indexes = [{'columns':['_airbyte_emitted_at'],'type':'btree'}],
    unique_key = '_airbyte_ab_id',
    schema = "test_normalization",
    tags = [ "top-level" ]
) }}
-- Final base SQL model
-- depends_on: {{ ref('arrays_ab3') }}
select
    array_of_strings,
    nested_array_parent,
    _airbyte_ab_id,
    _airbyte_emitted_at,
    {{ current_timestamp() }} as _airbyte_normalized_at,
    _airbyte_arrays_hashid
from {{ ref('arrays_ab3') }}
-- arrays from {{ source('test_normalization', '_airbyte_raw_arrays') }}
where 1 = 1

