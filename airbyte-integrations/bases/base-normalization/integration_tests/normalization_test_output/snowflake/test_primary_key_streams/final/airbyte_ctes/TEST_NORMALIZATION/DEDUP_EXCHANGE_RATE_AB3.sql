
  create or replace  view "AIRBYTE_DATABASE"._AIRBYTE_TEST_NORMALIZATION."DEDUP_EXCHANGE_RATE_AB3"  as (
    
-- SQL model to build a hash column based on the values of this record
select
    *,
    md5(cast(
    
    coalesce(cast(ID as 
    varchar
), '') || '-' || coalesce(cast(CURRENCY as 
    varchar
), '') || '-' || coalesce(cast(DATE as 
    varchar
), '') || '-' || coalesce(cast(TIMESTAMP_COL as 
    varchar
), '') || '-' || coalesce(cast("HKD@spéçiäl & characters" as 
    varchar
), '') || '-' || coalesce(cast(HKD_SPECIAL___CHARACTERS as 
    varchar
), '') || '-' || coalesce(cast(NZD as 
    varchar
), '') || '-' || coalesce(cast(USD as 
    varchar
), '')

 as 
    varchar
)) as _AIRBYTE_DEDUP_EXCHANGE_RATE_HASHID
from "AIRBYTE_DATABASE"._AIRBYTE_TEST_NORMALIZATION."DEDUP_EXCHANGE_RATE_AB2"
-- DEDUP_EXCHANGE_RATE
  );
