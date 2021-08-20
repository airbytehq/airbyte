
  create or replace  view "AIRBYTE_DATABASE"._AIRBYTE_TEST_NORMALIZATION."UNNEST_ALIAS_CHILDREN_AB3"  as (
    
-- SQL model to build a hash column based on the values of this record
select
    *,
    md5(cast(
    
    coalesce(cast(_AIRBYTE_UNNEST_ALIAS_HASHID as 
    varchar
), '') || '-' || coalesce(cast(AB_ID as 
    varchar
), '') || '-' || coalesce(cast(OWNER as 
    varchar
), '')

 as 
    varchar
)) as _AIRBYTE_CHILDREN_HASHID
from "AIRBYTE_DATABASE"._AIRBYTE_TEST_NORMALIZATION."UNNEST_ALIAS_CHILDREN_AB2"
-- CHILDREN at unnest_alias/children
  );
