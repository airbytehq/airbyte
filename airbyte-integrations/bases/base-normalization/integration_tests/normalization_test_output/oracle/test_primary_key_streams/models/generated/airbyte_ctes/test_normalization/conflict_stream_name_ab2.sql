{{ config(schema="test_normalization", tags=["top-level-intermediate"]) }}
-- SQL model to cast each column to its adequate SQL type converted from the JSON schema type
select
    cast(id as {{ dbt_utils.type_string() }}) as id,
    cast(conflict_stream_name as {{ type_json() }}) as conflict_stream_name,
    {{ quote('_AIRBYTE_EMITTED_AT') }}
from {{ ref('conflict_stream_name_ab1') }}
-- conflict_stream_name

