{{ config(schema="TEST_NORMALIZATION", tags=["nested"]) }}
-- Final base SQL model
select
    {{ QUOTE('_AIRBYTE_PARTITION_HASHID') }},
    CURRENCY,
    airbyte_emitted_at,
    {{ QUOTE('_AIRBYTE_DATA_HASHID') }}
from {{ ref('NESTED_STREAM_WITH_COMPLEX_COLUMNS_RESULTING_INTO_LONG_NAMES_PARTITION_DATA_AB3') }}
-- DATA at nested_stream_with_complex_columns_resulting_into_long_names/partition/DATA from {{ ref('NESTED_STREAM_WITH_COMPLEX_COLUMNS_RESULTING_INTO_LONG_NAMES_PARTITION') }}

