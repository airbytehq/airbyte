
  create view SYSTEM.DEDUP_CDC_EXCLUDED_AB4__dbt_tmp as
    
-- SQL model to prepare for deduplicating records based on the hash record column
select
  row_number() over (
    partition by AIRBYTE_DEDUP_CDC_EXCLUDED_HASHID
    order by airbyte_emitted_at asc
  ) as airbyte_row_num,
  tmp.*
from SYSTEM.DEDUP_CDC_EXCLUDED_AB3 tmp
-- DEDUP_CDC_EXCLUDED from "SYSTEM"."AIRBYTE_RAW_DEDUP_CDC_EXCLUDED"

