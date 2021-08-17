{{ config(schema="_AIRBYTE_TEST_NORMALIZATION", tags=["top-level-intermediate"]) }}
-- SQL model to cast each column to its adequate SQL type converted from the JSON schema type
select
    cast(ID as {{ dbt_utils.type_string() }}) as ID,
    cast(CONFLICT_STREAM_SCALAR as {{ dbt_utils.type_bigint() }}) as CONFLICT_STREAM_SCALAR,
    _airbyte_emitted_at
from {{ ref('CONFLICT_STREAM_SCALAR_AB1') }}
-- CONFLICT_STREAM_SCALAR

