{{ config(schema="_airbyte_test_normalization", tags=["top-level-intermediate"]) }}
-- SQL model to cast each column to its adequate SQL type converted from the JSON schema type
select
    cast(id as {{ dbt_utils.type_string() }}) as id,
    conflict_stream_array,
    _airbyte_emitted_at
from {{ ref('conflict_stream_array_ab1') }}
-- conflict_stream_array

