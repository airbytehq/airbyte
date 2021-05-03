{{ config(alias="nested_stream_with_complex_columns_669_data", schema="test_normalization", tags=["nested"]) }}
-- Final base SQL model
select
    _airbyte_partition_hashid,
    currency,
    _airbyte_emitted_at,
    _airbyte_data_hashid
from {{ ref('nested_stream_with_complex_col_669_data_ab3_ff0') }}
-- DATA at nested_stream_with_complex_columns_resulting_into_long_names/partition/DATA from {{ ref('nested_stream_with_complex_co_64a_partition_44f') }}

