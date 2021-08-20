

  create  table SYSTEM.DEDUP_EXCHANGE_RATE__dbt_tmp
  
  as
    
-- Final base SQL model
select
    ID,
    CURRENCY,
    "DATE",
    TIMESTAMP_COL,
    HKD_SPECIAL___CHARACTERS,
    HKD_SPECIAL___CHARACTERS_1,
    NZD,
    USD,
    airbyte_emitted_at,
    AIRBYTE_DEDUP_EXCHANGE_RATE_HASHID
from SYSTEM.DEDUP_EXCHANGE_RATE_SCD
-- DEDUP_EXCHANGE_RATE from "SYSTEM"."AIRBYTE_RAW_DEDUP_EXCHANGE_RATE"
where airbyte_active_row = 'Latest'