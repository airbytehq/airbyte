
  create or replace  view "AIRBYTE_DATABASE"._AIRBYTE_TEST_NORMALIZATION."UNNEST_ALIAS_AB3"  as (
    
-- SQL model to build a hash column based on the values of this record
select
    *,
    md5(cast(
    
    coalesce(cast(ID as 
    varchar
), '') || '-' || coalesce(cast(CHILDREN as 
    varchar
), '')

 as 
    varchar
)) as _AIRBYTE_UNNEST_ALIAS_HASHID
from "AIRBYTE_DATABASE"._AIRBYTE_TEST_NORMALIZATION."UNNEST_ALIAS_AB2"
-- UNNEST_ALIAS
  );
