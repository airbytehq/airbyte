
  create view _airbyte_test_normalization.`unnest_alias_ab3__dbt_tmp` as (
    
-- SQL model to build a hash column based on the values of this record
select
    *,
    md5(cast(concat(coalesce(cast(id as char), ''), '-', coalesce(cast(children as char), '')) as char)) as _airbyte_unnest_alias_hashid
from _airbyte_test_normalization.`unnest_alias_ab2`
-- unnest_alias
  );
