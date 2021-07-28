
  create or replace  view "AIRBYTE_DATABASE"._AIRBYTE_TEST_NORMALIZATION."DEDUP_CDC_EXCLUDED_AB4"  as (
    
-- SQL model to prepare for deduplicating records based on the hash record column
select
  *,
  row_number() over (
    partition by _AIRBYTE_DEDUP_CDC_EXCLUDED_HASHID
    order by _airbyte_emitted_at asc
  ) as _airbyte_row_num
from "AIRBYTE_DATABASE"._AIRBYTE_TEST_NORMALIZATION."DEDUP_CDC_EXCLUDED_AB3" as table_alias
-- DEDUP_CDC_EXCLUDED from "AIRBYTE_DATABASE".TEST_NORMALIZATION._AIRBYTE_RAW_DEDUP_CDC_EXCLUDED
  );
