
    
        
        insert into test_normalization.exchange_rate__dbt_tmp ("id", "currency", "date", "timestamp_col", "HKD@spéçiäl & characters", "HKD_special___characters", "NZD", "USD", "column___with__quotes", "datetime_tz", "datetime_no_tz", "time_tz", "time_no_tz", "_airbyte_ab_id", "_airbyte_emitted_at", "_airbyte_normalized_at", "_airbyte_exchange_rate_hashid")
  
-- Final base SQL model
-- depends_on: _airbyte_test_normalization.exchange_rate_ab3
select
    id,
    currency,
    date,
    timestamp_col,
    "HKD@spéçiäl & characters",
    HKD_special___characters,
    NZD,
    USD,
    "column___with__quotes",
    datetime_tz,
    datetime_no_tz,
    time_tz,
    time_no_tz,
    _airbyte_ab_id,
    _airbyte_emitted_at,
    now() as _airbyte_normalized_at,
    _airbyte_exchange_rate_hashid
from _airbyte_test_normalization.exchange_rate_ab3
-- exchange_rate from test_normalization._airbyte_raw_exchange_rate
where 1 = 1
  