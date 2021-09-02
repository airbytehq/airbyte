{{ config(schema="test_normalization", tags=["nested-intermediate"]) }}
-- SQL model to cast each column to its adequate SQL type converted from the JSON schema type
select
    {{ quote('_AIRBYTE_CONFLICT_STREAM_NAME_2_HASHID') }},
    cast(groups as {{ dbt_utils.type_string() }}) as groups,
    {{ quote('_AIRBYTE_EMITTED_AT') }}
from {{ ref('conflict_stream_name_conflict_stream_name_conflict_stream_name_ab1') }}
-- conflict_stream_name at conflict_stream_name/conflict_stream_name/conflict_stream_name

