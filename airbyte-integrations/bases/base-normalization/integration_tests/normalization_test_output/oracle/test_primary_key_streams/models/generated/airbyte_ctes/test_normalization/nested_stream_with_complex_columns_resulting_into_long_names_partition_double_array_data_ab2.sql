{{ config(schema="test_normalization", tags=["nested-intermediate"]) }}
-- SQL model to cast each column to its adequate SQL type converted from the JSON schema type
select
    {{ quote('_AIRBYTE_PARTITION_HASHID') }},
    cast(id as {{ dbt_utils.type_string() }}) as id,
    {{ quote('_AIRBYTE_EMITTED_AT') }}
from {{ ref('nested_stream_with_complex_columns_resulting_into_long_names_partition_double_array_data_ab1') }}
-- double_array_data at nested_stream_with_complex_columns_resulting_into_long_names/partition/double_array_data

