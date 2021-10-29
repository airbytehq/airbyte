

  create or replace table `dataline-integration-testing`.test_normalization.`unnest_alias_children`
  partition by timestamp_trunc(_airbyte_emitted_at, day)
  cluster by _airbyte_emitted_at
  OPTIONS()
  as (
    
-- Final base SQL model
select
    _airbyte_unnest_alias_hashid,
    ab_id,
    owner,
    _airbyte_ab_id,
    _airbyte_emitted_at,
    CURRENT_TIMESTAMP() as _airbyte_normalized_at,
    _airbyte_children_hashid
from `dataline-integration-testing`._airbyte_test_normalization.`unnest_alias_children_ab3`
-- children at unnest_alias/children from `dataline-integration-testing`.test_normalization.`unnest_alias`
where 1 = 1
  );
    