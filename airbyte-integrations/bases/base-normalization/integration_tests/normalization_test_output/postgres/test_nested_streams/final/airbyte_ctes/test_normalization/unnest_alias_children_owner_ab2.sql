
  create view "postgres"._airbyte_test_normalization."unnest_alias_children_owner_ab2__dbt_tmp" as (
    
-- SQL model to cast each column to its adequate SQL type converted from the JSON schema type
select
    _airbyte_children_hashid,
    cast(owner_id as 
    bigint
) as owner_id,
    _airbyte_emitted_at
from "postgres"._airbyte_test_normalization."unnest_alias_children_owner_ab1"
-- owner at unnest_alias/children/owner
  );
