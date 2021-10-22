{{ config(schema="_AIRBYTE_TEST_NORMALIZATION", tags=["nested-intermediate"]) }}
-- SQL model to cast each column to its adequate SQL type converted from the JSON schema type
select
    _AIRBYTE_PARTITION_HASHID,
    cast(ID as {{ dbt_utils.type_string() }}) as ID,
    _AIRBYTE_EMITTED_AT
from {{ ref('NESTED_STREAM_WITH_COMPLEX_COLUMNS_RESULTING_INTO_LONG_NAMES_PARTITION_DOUBLE_ARRAY_DATA_AB1') }}
-- DOUBLE_ARRAY_DATA at nested_stream_with_complex_columns_resulting_into_long_names/partition/double_array_data

