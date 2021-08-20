
  create view "postgres"._airbyte_test_normalization."unnest_alias_ab3__dbt_tmp" as (
    
-- SQL model to build a hash column based on the values of this record
select
    *,
    md5(cast(
    
    coalesce(cast("id" as 
    varchar
), '') || '-' || coalesce(cast(children as 
    varchar
), '')

 as 
    varchar
)) as _airbyte_unnest_alias_hashid
from "postgres"._airbyte_test_normalization."unnest_alias_ab2"
-- unnest_alias
  );
