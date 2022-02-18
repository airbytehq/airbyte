
      

  create  table "postgres".test_normalization."dedup_exchange_rate"
  as (
    
-- Final base SQL model
-- depends_on: "postgres".test_normalization."dedup_exchange_rate_scd"
select
    _airbyte_unique_key,
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
    _airbyte_dedup_exchange_rate_hashid
from "postgres".test_normalization."dedup_exchange_rate_scd"
-- dedup_exchange_rate from "postgres".test_normalization._airbyte_raw_dedup_exchange_rate
where 1 = 1
and _airbyte_active_row = 1

  );
  