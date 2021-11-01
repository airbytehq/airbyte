{{ config(
    unique_key = "{{ quote('_AIRBYTE_UNIQUE_KEY') }}",
    schema = "test_normalization",
    tags = [ "top-level" ]
) }}
-- Final base SQL model
select
    {{ quote('_AIRBYTE_UNIQUE_KEY') }},
    id,
    name,
    {{ quote('_AB_CDC_LSN') }},
    {{ quote('_AB_CDC_UPDATED_AT') }},
    {{ quote('_AB_CDC_DELETED_AT') }},
    {{ quote('_AIRBYTE_AB_ID') }},
    {{ quote('_AIRBYTE_EMITTED_AT') }},
    {{ current_timestamp() }} as {{ quote('_AIRBYTE_NORMALIZED_AT') }},
    {{ quote('_AIRBYTE_DEDUP_CDC_EXCLUDED_HASHID') }}
from {{ ref('dedup_cdc_excluded_scd') }}
-- dedup_cdc_excluded from {{ source('test_normalization', 'airbyte_raw_dedup_cdc_excluded') }}
where 1 = 1
and {{ quote('_AIRBYTE_ACTIVE_ROW') }} = 1
{{ incremental_clause(quote('_AIRBYTE_EMITTED_AT')) }}

