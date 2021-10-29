

  create  table
    test_normalization.`unnest_alias__dbt_tmp`
  as (
    
-- Final base SQL model
select
    id,
    children,
    _airbyte_ab_id,
    _airbyte_emitted_at,
    
    CURRENT_TIMESTAMP
 as _airbyte_normalized_at,
    _airbyte_unnest_alias_hashid
from _airbyte_test_normalization.`unnest_alias_ab3`
-- unnest_alias from test_normalization._airbyte_raw_unnest_alias
where 1 = 1

  )
