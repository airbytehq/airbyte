{{ config(schema="test_normalization", tags=["nested-intermediate"]) }}
-- SQL model to cast each column to its adequate SQL type converted from the JSON schema type
select
    {{ quote('_AIRBYTE_CONFLICT_STREAM_NAME_HASHID') }},
    cast(conflict_stream_name as {{ type_json() }}) as conflict_stream_name,
    {{ quote('_AIRBYTE_EMITTED_AT') }}
from {{ ref('conflict_stream_name_conflict_stream_name_ab1') }}
-- conflict_stream_name at conflict_stream_name/conflict_stream_name

