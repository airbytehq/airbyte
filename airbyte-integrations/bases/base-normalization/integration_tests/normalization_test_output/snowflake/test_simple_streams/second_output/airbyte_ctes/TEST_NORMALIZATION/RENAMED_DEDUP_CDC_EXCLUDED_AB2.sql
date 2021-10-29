
  create or replace  view "AIRBYTE_DATABASE"._AIRBYTE_TEST_NORMALIZATION."RENAMED_DEDUP_CDC_EXCLUDED_AB2"  as (
    
-- SQL model to cast each column to its adequate SQL type converted from the JSON schema type
select
    cast(ID as 
    bigint
) as ID,
    _AIRBYTE_AB_ID,
    _AIRBYTE_EMITTED_AT,
    convert_timezone('UTC', current_timestamp()) as _AIRBYTE_NORMALIZED_AT
from "AIRBYTE_DATABASE"._AIRBYTE_TEST_NORMALIZATION."RENAMED_DEDUP_CDC_EXCLUDED_AB1"
-- RENAMED_DEDUP_CDC_EXCLUDED
where 1 = 1

  );
