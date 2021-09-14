{{ config(schema="test_normalization", tags=["top-level-intermediate"]) }}
-- SQL model to parse JSON blob stored in a single column and extract into separated field columns as described by the JSON Schema
select
    {{ json_extract_scalar(quote('_AIRBYTE_DATA'), ['id'], ['id']) }} as id,
    {{ json_extract_scalar(quote('_AIRBYTE_DATA'), ['date'], ['date']) }} as {{ quote('DATE') }},
    {{ quote('_AIRBYTE_EMITTED_AT') }}
from {{ source('test_normalization_namespace', 'airbyte_raw_simple_stream_with_namespace_resulting_into_long_names') }} 
-- simple_stream_with_namespace_resulting_into_long_names

