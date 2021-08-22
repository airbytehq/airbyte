{{ config(schema="TEST_NORMALIZATION", tags=["top-level-intermediate"]) }}
-- SQL model to parse JSON blob stored in a single column and extract into separated field columns as described by the JSON Schema
select
    {{ json_extract_scalar('airbyte_data', ['id'], ['id']) }} as ID,
    {{ json_extract_array('airbyte_data', ['children'], ['children']) }} as CHILDREN,
    airbyte_emitted_at
from {{ source('TEST_NORMALIZATION', 'AIRBYTE_RAW_UNNEST_ALIAS') }} 
-- UNNEST_ALIAS

