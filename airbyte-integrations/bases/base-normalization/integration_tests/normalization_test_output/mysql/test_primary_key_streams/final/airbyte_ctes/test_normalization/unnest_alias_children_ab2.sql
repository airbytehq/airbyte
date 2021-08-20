
  create view _airbyte_test_normalization.`unnest_alias_children_ab2__dbt_tmp` as (
    
-- SQL model to cast each column to its adequate SQL type converted from the JSON schema type
select
    _airbyte_unnest_alias_hashid,
    cast(ab_id as 
    signed
) as ab_id,
    cast(`owner` as json) as `owner`,
    _airbyte_emitted_at
from _airbyte_test_normalization.`unnest_alias_children_ab1`
-- children at unnest_alias/children
  );
