{{ config(
    unique_key = "{{ quote('_AIRBYTE_UNIQUE_KEY') }}",
    schema = "test_normalization",
    tags = [ "top-level" ]
) }}
-- Final base SQL model
select
    {{ quote('_AIRBYTE_UNIQUE_KEY') }},
    id,
    {{ quote('_AIRBYTE_AB_ID') }},
    {{ quote('_AIRBYTE_EMITTED_AT') }},
    {{ current_timestamp() }} as {{ quote('_AIRBYTE_NORMALIZED_AT') }},
    {{ quote('_AIRBYTE_RENAMED_DEDUP_CDC_EXCLUDED_HASHID') }}
from {{ ref('renamed_dedup_cdc_excluded_scd') }}
-- renamed_dedup_cdc_excluded from {{ source('test_normalization', 'airbyte_raw_renamed_dedup_cdc_excluded') }}
where 1 = 1
and {{ quote('_AIRBYTE_ACTIVE_ROW') }} = 1
{{ incremental_clause(quote('_AIRBYTE_EMITTED_AT')) }}

