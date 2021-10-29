
      

  create  table "postgres".test_normalization."exchange_rate"
  as (
    
-- Final base SQL model
select
    "id",
    currency,
    "date",
    timestamp_col,
    "HKD@spéçiäl & characters",
    hkd_special___characters,
    nzd,
    usd,
    _airbyte_ab_id,
    _airbyte_emitted_at,
    now() as _airbyte_normalized_at,
    _airbyte_exchange_rate_hashid
from "postgres"._airbyte_test_normalization."exchange_rate_ab3"
-- exchange_rate from "postgres".test_normalization._airbyte_raw_exchange_rate
where 1 = 1

  );
  