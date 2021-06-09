{{ config(schema="_airbyte_test_normalization", tags=["nested-intermediate"]) }}
-- SQL model to cast each column to its adequate SQL type converted from the JSON schema type
select
    _airbyte_partition_hashid,
    cast({{ adapter.quote('id') }} as {{ dbt_utils.type_string() }}) as {{ adapter.quote('id') }},
    _airbyte_emitted_at
from {{ ref('nested_stream_with_c__ion_double_array_data_ab1') }}
-- double_array_data at nested_stream_with_complex_columns_resulting_into_long_names/partition/double_array_data

