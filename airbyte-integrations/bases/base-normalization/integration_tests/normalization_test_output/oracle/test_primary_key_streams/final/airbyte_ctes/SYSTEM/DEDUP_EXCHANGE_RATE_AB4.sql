
  create view SYSTEM.DEDUP_EXCHANGE_RATE_AB4__dbt_tmp as
    
-- SQL model to prepare for deduplicating records based on the hash record column
select
  row_number() over (
    partition by AIRBYTE_DEDUP_EXCHANGE_RATE_HASHID
    order by airbyte_emitted_at asc
  ) as airbyte_row_num,
  tmp.*
from SYSTEM.DEDUP_EXCHANGE_RATE_AB3 tmp
-- DEDUP_EXCHANGE_RATE from "SYSTEM"."AIRBYTE_RAW_DEDUP_EXCHANGE_RATE"

