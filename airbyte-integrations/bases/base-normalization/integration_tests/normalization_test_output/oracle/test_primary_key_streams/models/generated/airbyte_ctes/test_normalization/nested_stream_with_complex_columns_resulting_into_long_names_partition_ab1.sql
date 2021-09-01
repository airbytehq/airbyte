{{ config(schema="test_normalization", tags=["nested-intermediate"]) }}
-- SQL model to parse JSON blob stored in a single column and extract into separated field columns as described by the JSON Schema
select
    {{ quote('_AIRBYTE_NESTED_STREAM_WITH_COMPLEX_COLUMNS_RESULTING_INTO_LONG_NAMES_HASHID') }},
    {{ json_extract_array('partition', ['double_array_data'], ['double_array_data']) }} as double_array_data,
    {{ json_extract_array('partition', ['DATA'], ['DATA']) }} as data,
    {{ json_extract_array('partition', ['column`_\'with"_quotes'], ['column___with__quotes']) }} as column___with__quotes,
    {{ quote('_AIRBYTE_EMITTED_AT') }}
from {{ ref('nested_stream_with_complex_columns_resulting_into_long_names') }} 
where partition is not null
-- partition at nested_stream_with_complex_columns_resulting_into_long_names/partition

