
  create view _airbyte_test_normalization.`unnest_alias_children_owner_ab3__dbt_tmp` as (
    
-- SQL model to build a hash column based on the values of this record
select
    *,
    md5(cast(concat(coalesce(cast(_airbyte_children_hashid as char), ''), '-', coalesce(cast(owner_id as char), '')) as char)) as _airbyte_owner_hashid
from _airbyte_test_normalization.`unnest_alias_children_owner_ab2`
-- owner at unnest_alias/children/owner
  );
