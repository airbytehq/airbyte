
  create or replace  view "AIRBYTE_DATABASE"._AIRBYTE_TEST_NORMALIZATION."POS_DEDUP_CDCX_AB3"  as (
    
-- SQL model to build a hash column based on the values of this record
select
    md5(cast(coalesce(cast(ID as 
    varchar
), '') || '-' || coalesce(cast(NAME as 
    varchar
), '') || '-' || coalesce(cast(_AB_CDC_LSN as 
    varchar
), '') || '-' || coalesce(cast(_AB_CDC_UPDATED_AT as 
    varchar
), '') || '-' || coalesce(cast(_AB_CDC_DELETED_AT as 
    varchar
), '') || '-' || coalesce(cast(_AB_CDC_LOG_POS as 
    varchar
), '') as 
    varchar
)) as _AIRBYTE_POS_DEDUP_CDCX_HASHID,
    tmp.*
from "AIRBYTE_DATABASE"._AIRBYTE_TEST_NORMALIZATION."POS_DEDUP_CDCX_AB2" tmp
-- POS_DEDUP_CDCX
where 1 = 1
  );
