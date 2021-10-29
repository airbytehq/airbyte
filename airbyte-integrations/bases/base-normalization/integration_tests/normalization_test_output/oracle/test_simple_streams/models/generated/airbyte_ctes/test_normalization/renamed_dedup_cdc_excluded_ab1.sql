{{ config(
    unique_key = env_var('AIRBYTE_DEFAULT_UNIQUE_KEY', quote('_AIRBYTE_AB_ID')),
    schema = "test_normalization",
    tags = [ "top-level-intermediate" ]
) }}
-- SQL model to parse JSON blob stored in a single column and extract into separated field columns as described by the JSON Schema
select
    {{ json_extract_scalar(quote('_AIRBYTE_DATA'), ['id'], ['id']) }} as id,
    {{ quote('_AIRBYTE_AB_ID') }},
    {{ quote('_AIRBYTE_EMITTED_AT') }},
    {{ current_timestamp() }} as {{ quote('_AIRBYTE_NORMALIZED_AT') }}
from {{ source('test_normalization', 'airbyte_raw_renamed_dedup_cdc_excluded') }} 
-- renamed_dedup_cdc_excluded
where 1 = 1
{{ incremental_clause(quote('_AIRBYTE_EMITTED_AT')) }}

