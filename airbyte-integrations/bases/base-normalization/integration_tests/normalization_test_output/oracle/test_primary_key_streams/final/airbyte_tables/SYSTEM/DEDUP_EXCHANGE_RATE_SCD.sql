

  create  table SYSTEM.DEDUP_EXCHANGE_RATE_SCD__dbt_tmp
  
  as
    
-- SQL model to build a Type 2 Slowly Changing Dimension (SCD) table for each record identified by their primary key
select
    ID,
    CURRENCY,
    "DATE",
    TIMESTAMP_COL,
    HKD_SPECIAL___CHARACTERS,
    HKD_SPECIAL___CHARACTERS_1,
    NZD,
    USD,
    "DATE" as airbyte_start_at,
    lag("DATE") over (
        partition by ID, CURRENCY, cast(NZD as varchar(1000))
        order by "DATE" desc, airbyte_emitted_at desc
    ) as airbyte_end_at,
    coalesce(cast(lag("DATE") over (
        partition by ID, CURRENCY, cast(NZD as varchar(1000))
        order by "DATE" desc, airbyte_emitted_at desc
    ) as varchar(200)), 'Latest') as airbyte_active_row,
    airbyte_emitted_at,
    AIRBYTE_DEDUP_EXCHANGE_RATE_HASHID
from SYSTEM.DEDUP_EXCHANGE_RATE_AB4
-- DEDUP_EXCHANGE_RATE from "SYSTEM"."AIRBYTE_RAW_DEDUP_EXCHANGE_RATE"
where airbyte_row_num = 1