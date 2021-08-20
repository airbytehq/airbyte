{{ config(schema="SYSTEM", tags=["nested"]) }}
-- Final base SQL model
select
    AIRBYTE_PARTITION_HASHID,
    ID,
    airbyte_emitted_at,
    AIRBYTE_DOUBLE_ARRAY_DATA_HASHID
from {{ ref('NESTED_STREAM_WITH_COMPLEX_COLUMNS_RESULTING_INTO_LONG_NAMES_PARTITION_DOUBLE_ARRAY_DATA_AB3') }}
-- DOUBLE_ARRAY_DATA at nested_stream_with_complex_columns_resulting_into_long_names/partition/double_array_data from {{ ref('NESTED_STREAM_WITH_COMPLEX_COLUMNS_RESULTING_INTO_LONG_NAMES_PARTITION') }}

