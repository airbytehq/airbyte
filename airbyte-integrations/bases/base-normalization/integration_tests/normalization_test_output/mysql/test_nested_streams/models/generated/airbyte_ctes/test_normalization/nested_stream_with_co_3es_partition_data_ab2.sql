{{ config(schema="_airbyte_test_normalization", tags=["nested-intermediate"]) }}
-- SQL model to cast each column to its adequate SQL type converted from the JSON schema type
select
    _airbyte_partition_hashid,
    cast(currency as {{ dbt_utils.type_string() }}) as currency,
    _airbyte_emitted_at
from {{ ref('nested_stream_with_co_3es_partition_data_ab1') }}
-- DATA at nested_stream_with_complex_columns_resulting_into_long_names/partition/DATA

