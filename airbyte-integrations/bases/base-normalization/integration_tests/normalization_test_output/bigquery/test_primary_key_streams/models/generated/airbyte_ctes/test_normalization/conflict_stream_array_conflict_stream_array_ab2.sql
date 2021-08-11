{{ config(schema="_airbyte_test_normalization", tags=["nested-intermediate"]) }}
-- SQL model to cast each column to its adequate SQL type converted from the JSON schema type
select
    _airbyte_conflict_stream_array_hashid,
    conflict_stream_name,
    _airbyte_emitted_at
from {{ ref('conflict_stream_array_conflict_stream_array_ab1') }}
-- conflict_stream_array at conflict_stream_array/conflict_stream_array

