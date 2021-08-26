
  create view _airbyte_test_normalization.`unnest_alias_children_ab3__dbt_tmp` as (
    
-- SQL model to build a hash column based on the values of this record
select
    *,
    md5(cast(concat(coalesce(cast(_airbyte_unnest_alias_hashid as char), ''), '-', coalesce(cast(ab_id as char), ''), '-', coalesce(cast(`owner` as char), '')) as char)) as _airbyte_children_hashid
from _airbyte_test_normalization.`unnest_alias_children_ab2`
-- children at unnest_alias/children
  );
