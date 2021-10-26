

  create  table "postgres".test_normalization."dedup_exchange_rate__dbt_tmp"
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
    _airbyte_emitted_at,
    _airbyte_dedup_exchange_rate_hashid
from "postgres".test_normalization."dedup_exchange_rate_scd"
-- dedup_exchange_rate from "postgres".test_normalization._airbyte_raw_dedup_exchange_rate
where _airbyte_active_row = 1
  );