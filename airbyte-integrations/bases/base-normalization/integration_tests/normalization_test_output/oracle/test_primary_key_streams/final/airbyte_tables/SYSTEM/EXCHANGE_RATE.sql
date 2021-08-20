

  create  table SYSTEM.EXCHANGE_RATE__dbt_tmp
  
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
    AIRBYTE_EXCHANGE_RATE_HASHID
from SYSTEM.EXCHANGE_RATE_AB3
-- EXCHANGE_RATE from "SYSTEM"."AIRBYTE_RAW_EXCHANGE_RATE"