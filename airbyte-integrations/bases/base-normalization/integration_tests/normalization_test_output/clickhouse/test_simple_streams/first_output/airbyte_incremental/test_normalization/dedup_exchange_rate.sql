
      
    
        
        insert into test_normalization.dedup_exchange_rate ("_airbyte_unique_key", "id", "currency", "date", "timestamp_col", "HKD@spéçiäl & characters", "HKD_special___characters", "NZD", "USD", "_airbyte_ab_id", "_airbyte_emitted_at", "_airbyte_normalized_at", "_airbyte_dedup_exchange_rate_hashid")
  
-- Final base SQL model
-- depends_on: test_normalization.dedup_exchange_rate_scd
select
    _airbyte_unique_key,
    id,
    currency,
    date,
    timestamp_col,
    "HKD@spéçiäl & characters",
    HKD_special___characters,
    NZD,
    USD,
    _airbyte_ab_id,
    _airbyte_emitted_at,
    now() as _airbyte_normalized_at,
    _airbyte_dedup_exchange_rate_hashid
from test_normalization.dedup_exchange_rate_scd
-- dedup_exchange_rate from test_normalization._airbyte_raw_dedup_exchange_rate
where 1 = 1
and _airbyte_active_row = 1

  
  