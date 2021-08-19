{{ config(schema="_AIRBYTE_TEST_NORMALIZATION", tags=["nested-intermediate"]) }}
-- SQL model to parse JSON blob stored in a single column and extract into separated field columns as described by the JSON Schema
select
    _AIRBYTE_NESTED_STREAM_WITH_COMPLEX_COLUMNS_RESULTING_INTO_LONG_NAMES_HASHID,
    {{ json_extract_array('PARTITION', ['double_array_data'], ['double_array_data']) }} as DOUBLE_ARRAY_DATA,
    {{ json_extract_array('PARTITION', ['DATA'], ['DATA']) }} as DATA,
    {{ json_extract_array('PARTITION', ['column`_\'with"_quotes'], ['column___with__quotes']) }} as {{ adapter.quote('column`_\'with""_quotes') }},
    _airbyte_emitted_at
from {{ ref('NESTED_STREAM_WITH_COMPLEX_COLUMNS_RESULTING_INTO_LONG_NAMES') }} as table_alias
where PARTITION is not null
-- PARTITION at nested_stream_with_complex_columns_resulting_into_long_names/partition

