

  create or replace table `dataline-integration-testing`.test_normalization.`exchange_rate`
  
  
  OPTIONS()
  as (
    
-- Final base SQL model
select
    id,
    currency,
    date,
    HKD,
    NZD,
    USD,
    _airbyte_emitted_at,
    _airbyte_exchange_rate_hashid
from `dataline-integration-testing`._airbyte_test_normalization.`exchange_rate_ab3`
-- exchange_rate from `dataline-integration-testing`.test_normalization._airbyte_raw_exchange_rate
  );
    