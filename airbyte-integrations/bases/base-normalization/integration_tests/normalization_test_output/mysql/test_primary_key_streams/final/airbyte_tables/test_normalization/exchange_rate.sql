

  create  table
    test_normalization.`exchange_rate__dbt_tmp`
  as (
    
-- Final base SQL model
select
    id,
    currency,
    `date`,
    `HKD@spéçiäl & characters`,
    hkd_special___characters,
    nzd,
    usd,
    _airbyte_emitted_at,
    _airbyte_exchange_rate_hashid
from _airbyte_test_normalization.`exchange_rate_ab3`
-- exchange_rate from test_normalization._airbyte_raw_exchange_rate
  )
