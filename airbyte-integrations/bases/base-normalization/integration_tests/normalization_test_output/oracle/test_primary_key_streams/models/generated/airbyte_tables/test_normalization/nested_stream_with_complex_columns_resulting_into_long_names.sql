{{ config(schema="test_normalization", tags=["top-level"]) }}
-- Final base SQL model
select
    id,
    {{ QUOTE('DATE') }},
    partition,
    airbyte_emitted_at,
    {{ QUOTE('_AIRBYTE_NESTED_STREAM_WITH_COMPLEX_COLUMNS_RESULTING_INTO_LONG_NAMES_HASHID') }}
from {{ ref('nested_stream_with_complex_columns_resulting_into_long_names_scd') }}
-- nested_stream_with_complex_columns_resulting_into_long_names from {{ source('test_normalization', 'airbyte_raw_nested_stream_with_complex_columns_resulting_into_long_names') }}
where airbyte_active_row = 'Latest'

