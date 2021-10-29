

  create or replace table `dataline-integration-testing`.test_normalization.`exchange_rate`
  partition by timestamp_trunc(_airbyte_emitted_at, day)
  cluster by _airbyte_emitted_at
  OPTIONS()
  as (
    
-- Final base SQL model
select
    id,
    currency,
    date,
    timestamp_col,
    HKD_special___characters,
    HKD_special___characters_1,
    NZD,
    USD,
    _airbyte_ab_id,
    _airbyte_emitted_at,
    CURRENT_TIMESTAMP() as _airbyte_normalized_at,
    _airbyte_exchange_rate_hashid
from `dataline-integration-testing`._airbyte_test_normalization.`exchange_rate_ab3`
-- exchange_rate from `dataline-integration-testing`.test_normalization._airbyte_raw_exchange_rate
where 1 = 1

  );
  