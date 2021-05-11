{{ config(alias="nested_stream_with_complex_columns_resulting_into_long_names_partition_e78_double_array_data_ab2", schema="_airbyte_test_normalization", tags=["nested-intermediate"]) }}
-- SQL model to cast each column to its adequate SQL type converted from the JSON schema type
select
    _airbyte_partition_hashid,
    cast(id as {{ dbt_utils.type_string() }}) as id,
    _airbyte_emitted_at
from {{ ref('nested_stream_with_complex_columns_resulting_into_long_names_partition_e78_double_array_data_ab1_a78') }}
-- double_array_data at nested_stream_with_complex_columns_resulting_into_long_names/partition/double_array_data

