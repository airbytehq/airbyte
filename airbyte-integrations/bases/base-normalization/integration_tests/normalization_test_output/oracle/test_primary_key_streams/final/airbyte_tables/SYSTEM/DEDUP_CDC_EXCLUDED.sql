

  create  table SYSTEM.DEDUP_CDC_EXCLUDED__dbt_tmp
  
  as
    
-- Final base SQL model
select
    ID,
    NAME,
    "_AB_CDC_LSN",
    "_AB_CDC_UPDATED_AT",
    "_AB_CDC_DELETED_AT",
    airbyte_emitted_at,
    AIRBYTE_DEDUP_CDC_EXCLUDED_HASHID
from SYSTEM.DEDUP_CDC_EXCLUDED_SCD
-- DEDUP_CDC_EXCLUDED from "SYSTEM"."AIRBYTE_RAW_DEDUP_CDC_EXCLUDED"
where airbyte_active_row = 'Latest'