

      create or replace transient table "AIRBYTE_DATABASE".TEST_NORMALIZATION."DEDUP_CDC_EXCLUDED"  as
      (
-- Final base SQL model
select
    ID,
    NAME,
    _AB_CDC_LSN,
    _AB_CDC_UPDATED_AT,
    _AB_CDC_DELETED_AT,
    _airbyte_emitted_at,
    _AIRBYTE_DEDUP_CDC_EXCLUDED_HASHID
from "AIRBYTE_DATABASE".TEST_NORMALIZATION."DEDUP_CDC_EXCLUDED_SCD"
-- DEDUP_CDC_EXCLUDED from "AIRBYTE_DATABASE".TEST_NORMALIZATION._AIRBYTE_RAW_DEDUP_CDC_EXCLUDED
where _airbyte_active_row = True
      );
    