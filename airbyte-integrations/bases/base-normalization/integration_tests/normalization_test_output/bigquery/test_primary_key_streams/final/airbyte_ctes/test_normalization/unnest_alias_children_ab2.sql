

  create or replace view `dataline-integration-testing`._airbyte_test_normalization.`unnest_alias_children_ab2`
  OPTIONS()
  as 
-- SQL model to cast each column to its adequate SQL type converted from the JSON schema type
select
    _airbyte_unnest_alias_hashid,
    cast(ab_id as 
    int64
) as ab_id,
    cast(owner as 
    string
) as owner,
    _airbyte_emitted_at
from `dataline-integration-testing`._airbyte_test_normalization.`unnest_alias_children_ab1`
-- children at unnest_alias/children;

