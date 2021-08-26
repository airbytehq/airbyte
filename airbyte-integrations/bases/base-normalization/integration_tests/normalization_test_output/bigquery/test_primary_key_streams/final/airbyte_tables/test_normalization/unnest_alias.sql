

  create or replace table `dataline-integration-testing`.test_normalization.`unnest_alias`
  
  
  OPTIONS()
  as (
    
-- Final base SQL model
select
    id,
    children,
    _airbyte_emitted_at,
    _airbyte_unnest_alias_hashid
from `dataline-integration-testing`._airbyte_test_normalization.`unnest_alias_ab3`
-- unnest_alias from `dataline-integration-testing`.test_normalization._airbyte_raw_unnest_alias
  );
    