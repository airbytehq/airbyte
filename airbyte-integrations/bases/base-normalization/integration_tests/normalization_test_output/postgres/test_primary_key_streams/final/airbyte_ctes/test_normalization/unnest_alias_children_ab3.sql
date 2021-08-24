
  create view "postgres"._airbyte_test_normalization."unnest_alias_children_ab3__dbt_tmp" as (
    
-- SQL model to build a hash column based on the values of this record
select
    *,
    md5(cast(
    
    coalesce(cast(_airbyte_unnest_alias_hashid as 
    varchar
), '') || '-' || coalesce(cast(ab_id as 
    varchar
), '') || '-' || coalesce(cast("owner" as 
    varchar
), '')

 as 
    varchar
)) as _airbyte_children_hashid
from "postgres"._airbyte_test_normalization."unnest_alias_children_ab2"
-- children at unnest_alias/children
  );
