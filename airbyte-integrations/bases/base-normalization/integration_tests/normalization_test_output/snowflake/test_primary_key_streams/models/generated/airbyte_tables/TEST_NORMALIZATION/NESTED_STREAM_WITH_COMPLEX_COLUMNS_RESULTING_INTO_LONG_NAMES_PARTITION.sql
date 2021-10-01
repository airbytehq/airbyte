{{ config(schema="TEST_NORMALIZATION", tags=["nested"]) }}
-- Final base SQL model
select
    _AIRBYTE_NESTED_STREAM_WITH_COMPLEX_COLUMNS_RESULTING_INTO_LONG_NAMES_HASHID,
    DOUBLE_ARRAY_DATA,
    DATA,
    {{ adapter.quote('column`_\'with""_quotes') }},
    _AIRBYTE_EMITTED_AT,
    _AIRBYTE_PARTITION_HASHID
from {{ ref('NESTED_STREAM_WITH_COMPLEX_COLUMNS_RESULTING_INTO_LONG_NAMES_PARTITION_AB3') }}
-- PARTITION at nested_stream_with_complex_columns_resulting_into_long_names/partition from {{ ref('NESTED_STREAM_WITH_COMPLEX_COLUMNS_RESULTING_INTO_LONG_NAMES') }}

