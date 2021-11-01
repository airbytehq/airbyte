
  create or replace  view "AIRBYTE_DATABASE"._AIRBYTE_TEST_NORMALIZATION."DEDUP_CDC_EXCLUDED_AB3"  as (
    
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
), '') as 
    varchar
)) as _AIRBYTE_DEDUP_CDC_EXCLUDED_HASHID,
    tmp.*
from "AIRBYTE_DATABASE"._AIRBYTE_TEST_NORMALIZATION."DEDUP_CDC_EXCLUDED_AB2" tmp
-- DEDUP_CDC_EXCLUDED
where 1 = 1

  );
