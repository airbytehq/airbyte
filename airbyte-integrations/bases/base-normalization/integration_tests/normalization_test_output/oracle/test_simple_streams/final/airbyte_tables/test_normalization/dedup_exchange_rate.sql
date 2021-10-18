

  create  table test_normalization.dedup_exchange_rate__dbt_tmp
  
  as
    
-- Final base SQL model
select
    id,
    currency,
    "DATE",
    timestamp_col,
    hkd_special___characters,
    hkd_special___characters_1,
    nzd,
    usd,
    "_AIRBYTE_EMITTED_AT",
    "_AIRBYTE_DEDUP_EXCHANGE_RATE_HASHID"
from test_normalization.dedup_exchange_rate_scd
-- dedup_exchange_rate from test_normalization.airbyte_raw_dedup_exchange_rate
where "_AIRBYTE_ACTIVE_ROW" = 1