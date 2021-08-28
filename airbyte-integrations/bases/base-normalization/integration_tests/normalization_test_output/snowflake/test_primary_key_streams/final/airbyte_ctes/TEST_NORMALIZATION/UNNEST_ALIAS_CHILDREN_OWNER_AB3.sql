
  create or replace  view "AIRBYTE_DATABASE"._AIRBYTE_TEST_NORMALIZATION."UNNEST_ALIAS_CHILDREN_OWNER_AB3"  as (
    
-- SQL model to build a hash column based on the values of this record
select
    *,
    md5(cast(
    
    coalesce(cast(_AIRBYTE_CHILDREN_HASHID as 
    varchar
), '') || '-' || coalesce(cast(OWNER_ID as 
    varchar
), '')

 as 
    varchar
)) as _AIRBYTE_OWNER_HASHID
from "AIRBYTE_DATABASE"._AIRBYTE_TEST_NORMALIZATION."UNNEST_ALIAS_CHILDREN_OWNER_AB2"
-- OWNER at unnest_alias/children/owner
  );
