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
    NAME,
    _AB_CDC_LSN,
    _AB_CDC_UPDATED_AT,
    _AB_CDC_DELETED_AT,
    _AB_CDC_LOG_POS,
    _AIRBYTE_AB_ID,
    _AIRBYTE_EMITTED_AT,
    {{ current_timestamp() }} as _AIRBYTE_NORMALIZED_AT,
    _AIRBYTE_POS_DEDUP_CDCX_HASHID
from {{ ref('POS_DEDUP_CDCX_SCD') }}
-- POS_DEDUP_CDCX from {{ source('TEST_NORMALIZATION', '_AIRBYTE_RAW_POS_DEDUP_CDCX') }}
where 1 = 1
and _AIRBYTE_ACTIVE_ROW = 1

