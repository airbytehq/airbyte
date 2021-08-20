{{ config(schema="SYSTEM", tags=["nested"]) }}
-- Final base SQL model
select
    AIRBYTE_NESTED_STREAM_WITH_COMPLEX_COLUMNS_RESULTING_INTO_LONG_NAMES_HASHID,
    DOUBLE_ARRAY_DATA,
    DATA,
    COLUMN___WITH__QUOTES,
    airbyte_emitted_at,
    AIRBYTE_PARTITION_HASHID
from {{ ref('NESTED_STREAM_WITH_COMPLEX_COLUMNS_RESULTING_INTO_LONG_NAMES_PARTITION_AB3') }}
-- PARTITION at nested_stream_with_complex_columns_resulting_into_long_names/partition from {{ ref('NESTED_STREAM_WITH_COMPLEX_COLUMNS_RESULTING_INTO_LONG_NAMES') }}

