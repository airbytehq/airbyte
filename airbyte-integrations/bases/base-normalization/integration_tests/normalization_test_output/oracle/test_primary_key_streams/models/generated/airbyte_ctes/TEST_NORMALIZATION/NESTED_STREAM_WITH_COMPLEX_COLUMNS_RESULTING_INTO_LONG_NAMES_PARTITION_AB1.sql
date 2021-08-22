{{ config(schema="TEST_NORMALIZATION", tags=["nested-intermediate"]) }}
-- SQL model to parse JSON blob stored in a single column and extract into separated field columns as described by the JSON Schema
select
    {{ QUOTE('_AIRBYTE_NESTED_STREAM_WITH_COMPLEX_COLUMNS_RESULTING_INTO_LONG_NAMES_HASHID') }},
    {{ json_extract_array('PARTITION', ['double_array_data'], ['double_array_data']) }} as DOUBLE_ARRAY_DATA,
    {{ json_extract_array('PARTITION', ['DATA'], ['DATA']) }} as DATA,
    {{ json_extract_array('PARTITION', ['column`_\'with"_quotes'], ['column___with__quotes']) }} as COLUMN___WITH__QUOTES,
    airbyte_emitted_at
from {{ ref('NESTED_STREAM_WITH_COMPLEX_COLUMNS_RESULTING_INTO_LONG_NAMES') }} 
where PARTITION is not null
-- PARTITION at nested_stream_with_complex_columns_resulting_into_long_names/partition

