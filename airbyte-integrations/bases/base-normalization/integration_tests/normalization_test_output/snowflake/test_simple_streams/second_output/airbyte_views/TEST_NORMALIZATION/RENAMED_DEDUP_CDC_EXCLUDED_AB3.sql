
  create or replace  view "AIRBYTE_DATABASE"._AIRBYTE_TEST_NORMALIZATION."RENAMED_DEDUP_CDC_EXCLUDED_AB3"  as (
    
-- SQL model to build a hash column based on the values of this record
select
    md5(cast(coalesce(cast(ID as 
    varchar
), '') as 
    varchar
)) as _AIRBYTE_RENAMED_DEDUP_CDC_EXCLUDED_HASHID,
    tmp.*
from "AIRBYTE_DATABASE"._AIRBYTE_TEST_NORMALIZATION."RENAMED_DEDUP_CDC_EXCLUDED_AB2" tmp
-- RENAMED_DEDUP_CDC_EXCLUDED
where 1 = 1

  );
