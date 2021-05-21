{{ config(alias="nested_stream_with_complex_columns_resulting_into_long_names_64a_partition", schema="test_normalization", tags=["nested"]) }}
-- Final base SQL model
select
    _airbyte_nested_stream_with_complex_columns_resulting_into_long_names_hashid,
    double_array_data,
    DATA,
    _airbyte_emitted_at,
    _airbyte_partition_hashid
from {{ ref('nested_stream_with_complex_columns_resulting_into_long_names_64a_partition_ab3_db2') }}
-- partition at nested_stream_with_complex_columns_resulting_into_long_names/partition from {{ ref('nested_stream_with_complex_columns_resulting_into_long_names_d67') }}

