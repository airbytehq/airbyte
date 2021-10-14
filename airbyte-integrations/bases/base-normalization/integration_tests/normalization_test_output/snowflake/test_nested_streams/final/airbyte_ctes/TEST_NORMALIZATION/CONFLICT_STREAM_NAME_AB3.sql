
  create or replace  view "AIRBYTE_DATABASE"._AIRBYTE_TEST_NORMALIZATION."CONFLICT_STREAM_NAME_AB3"  as (
    
-- SQL model to build a hash column based on the values of this record
select
    md5(cast(coalesce(cast(ID as 
    varchar
), '') || '-' || coalesce(cast(CONFLICT_STREAM_NAME as 
    varchar
), '') as 
    varchar
)) as _AIRBYTE_CONFLICT_STREAM_NAME_HASHID,
    tmp.*
from "AIRBYTE_DATABASE"._AIRBYTE_TEST_NORMALIZATION."CONFLICT_STREAM_NAME_AB2" tmp
-- CONFLICT_STREAM_NAME
  );
