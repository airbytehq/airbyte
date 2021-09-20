{{ config(schema="test_normalization", tags=["top-level-intermediate"]) }}
-- SQL model to parse JSON blob stored in a single column and extract into separated field columns as described by the JSON Schema
select
    {{ json_extract_scalar(quote('_AIRBYTE_DATA'), ['id'], ['id']) }} as id,
    {{ json_extract_array(quote('_AIRBYTE_DATA'), ['children'], ['children']) }} as children,
    {{ quote('_AIRBYTE_EMITTED_AT') }}
from {{ source('test_normalization', 'airbyte_raw_unnest_alias') }} 
-- unnest_alias

