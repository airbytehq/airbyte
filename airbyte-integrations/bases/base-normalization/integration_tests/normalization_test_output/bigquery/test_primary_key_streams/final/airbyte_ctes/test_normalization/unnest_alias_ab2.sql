

  create or replace view `dataline-integration-testing`._airbyte_test_normalization.`unnest_alias_ab2`
  OPTIONS()
  as 
-- SQL model to cast each column to its adequate SQL type converted from the JSON schema type
select
    cast(id as 
    int64
) as id,
    children,
    _airbyte_emitted_at
from `dataline-integration-testing`._airbyte_test_normalization.`unnest_alias_ab1`
-- unnest_alias;

