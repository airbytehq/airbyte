{{ config(
    cluster_by = ["_AIRBYTE_UNIQUE_KEY", "_AIRBYTE_EMITTED_AT"],
    unique_key = "_AIRBYTE_UNIQUE_KEY",
    schema = "TEST_NORMALIZATION",
    tags = [ "top-level" ]
) }}
-- Final base SQL model
select
    _AIRBYTE_UNIQUE_KEY,
    ID,
    _AIRBYTE_AB_ID,
    _AIRBYTE_EMITTED_AT,
    {{ current_timestamp() }} as _AIRBYTE_NORMALIZED_AT,
    _AIRBYTE_RENAMED_DEDUP_CDC_EXCLUDED_HASHID
from {{ ref('RENAMED_DEDUP_CDC_EXCLUDED_SCD') }}
-- RENAMED_DEDUP_CDC_EXCLUDED from {{ source('TEST_NORMALIZATION', '_AIRBYTE_RAW_RENAMED_DEDUP_CDC_EXCLUDED') }}
where 1 = 1
and _AIRBYTE_ACTIVE_ROW = 1
{{ incremental_clause('_AIRBYTE_EMITTED_AT') }}

