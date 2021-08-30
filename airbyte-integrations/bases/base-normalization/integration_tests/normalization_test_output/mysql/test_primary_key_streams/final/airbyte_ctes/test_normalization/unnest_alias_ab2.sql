
  create view _airbyte_test_normalization.`unnest_alias_ab2__dbt_tmp` as (
    
-- SQL model to cast each column to its adequate SQL type converted from the JSON schema type
select
    cast(id as 
    signed
) as id,
    children,
    _airbyte_emitted_at
from _airbyte_test_normalization.`unnest_alias_ab1`
-- unnest_alias
  );
