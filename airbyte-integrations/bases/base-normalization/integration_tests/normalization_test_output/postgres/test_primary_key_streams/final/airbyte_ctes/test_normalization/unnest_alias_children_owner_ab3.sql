
  create view "postgres"._airbyte_test_normalization."unnest_alias_children_owner_ab3__dbt_tmp" as (
    
-- SQL model to build a hash column based on the values of this record
select
    *,
    md5(cast(
    
    coalesce(cast(_airbyte_children_hashid as 
    varchar
), '') || '-' || coalesce(cast(owner_id as 
    varchar
), '')

 as 
    varchar
)) as _airbyte_owner_hashid
from "postgres"._airbyte_test_normalization."unnest_alias_children_owner_ab2"
-- owner at unnest_alias/children/owner
  );
