

  create  table
    test_normalization.`unnest_alias_children__dbt_tmp`
  as (
    
-- Final base SQL model
select
    _airbyte_unnest_alias_hashid,
    ab_id,
    `owner`,
    _airbyte_emitted_at,
    _airbyte_children_hashid
from _airbyte_test_normalization.`unnest_alias_children_ab3`
-- children at unnest_alias/children from test_normalization.`unnest_alias`
  )
