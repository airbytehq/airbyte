
      

  create  table
    "normalization_tests".test_normalization_spffv."dedup_exchange_rate"
    
    
      compound sortkey(_airbyte_unique_key,_airbyte_emitted_at)
    
  as (
    
-- Final base SQL model
-- depends_on: "normalization_tests".test_normalization_spffv."dedup_exchange_rate_scd"
select
    _airbyte_unique_key,
    id,
    currency,
    date,
    timestamp_col,
    "hkd@spéçiäl & characters",
    hkd_special___characters,
    nzd,
    usd,
    _airbyte_ab_id,
    _airbyte_emitted_at,
    getdate() as _airbyte_normalized_at,
    _airbyte_dedup_exchange_rate_hashid
from "normalization_tests".test_normalization_spffv."dedup_exchange_rate_scd"
-- dedup_exchange_rate from "normalization_tests".test_normalization_spffv._airbyte_raw_dedup_exchange_rate
where 1 = 1
and _airbyte_active_row = 1

  );
  