{{ config(schema="SYSTEM", tags=["nested-intermediate"]) }}
-- SQL model to parse JSON blob stored in a single column and extract into separated field columns as described by the JSON Schema
select
    AIRBYTE_NESTED_STREAM_WITH_COMPLEX_COLUMNS_RESULTING_INTO_LONG_NAMES_HASHID,
    {{ json_extract_array('PARTITION', ['double_array_data']) }} as DOUBLE_ARRAY_DATA,
    {{ json_extract_array('PARTITION', ['DATA']) }} as DATA,
    {{ json_extract_array('PARTITION', ['column`_\'with"_quotes']) }} as COLUMN___WITH__QUOTES,
    airbyte_emitted_at
from {{ ref('NESTED_STREAM_WITH_COMPLEX_COLUMNS_RESULTING_INTO_LONG_NAMES') }}
where PARTITION is not null
-- PARTITION at nested_stream_with_complex_columns_resulting_into_long_names/partition

