{{ config(
    cluster_by = ["_AIRBYTE_EMITTED_AT"],
    unique_key = env_var('AIRBYTE_DEFAULT_UNIQUE_KEY', '_AIRBYTE_AB_ID'),
    schema = "_AIRBYTE_TEST_NORMALIZATION_NAMESPACE",
    tags = [ "top-level-intermediate" ]
) }}
-- SQL model to cast each column to its adequate SQL type converted from the JSON schema type
select
    cast(ID as {{ dbt_utils.type_string() }}) as ID,
    cast(DATE as {{ dbt_utils.type_string() }}) as DATE,
    _AIRBYTE_AB_ID,
    _AIRBYTE_EMITTED_AT,
    {{ current_timestamp() }} as _AIRBYTE_NORMALIZED_AT
from {{ ref('SIMPLE_STREAM_WITH_NAMESPACE_RESULTING_INTO_LONG_NAMES_AB1') }}
-- SIMPLE_STREAM_WITH_NAMESPACE_RESULTING_INTO_LONG_NAMES
where 1 = 1

