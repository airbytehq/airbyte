
  create or replace  view "AIRBYTE_DATABASE"._AIRBYTE_TEST_NORMALIZATION."DEDUP_EXCHANGE_RATE_AB4"  as (
    
-- SQL model to prepare for deduplicating records based on the hash record column
select
  *,
  row_number() over (
    partition by _AIRBYTE_DEDUP_EXCHANGE_RATE_HASHID
    order by _airbyte_emitted_at asc
  ) as _airbyte_row_num
from "AIRBYTE_DATABASE"._AIRBYTE_TEST_NORMALIZATION."DEDUP_EXCHANGE_RATE_AB3"
-- DEDUP_EXCHANGE_RATE from "AIRBYTE_DATABASE".TEST_NORMALIZATION._AIRBYTE_RAW_DEDUP_EXCHANGE_RATE
  );
