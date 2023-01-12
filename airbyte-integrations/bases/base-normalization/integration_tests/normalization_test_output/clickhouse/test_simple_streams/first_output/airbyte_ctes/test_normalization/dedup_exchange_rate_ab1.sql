

  create view _airbyte_test_normalization.dedup_exchange_rate_ab1 
  
  as (
    
-- SQL model to parse JSON blob stored in a single column and extract into separated field columns as described by the JSON Schema
-- depends_on: test_normalization._airbyte_raw_dedup_exchange_rate
select
    JSONExtractRaw(assumeNotNull(_airbyte_data), 'id') as id,
    JSONExtractRaw(assumeNotNull(_airbyte_data), 'currency') as currency,
    JSONExtractRaw(assumeNotNull(_airbyte_data), 'date') as date,
    JSONExtractRaw(assumeNotNull(_airbyte_data), 'timestamp_col') as timestamp_col,
    JSONExtractRaw(assumeNotNull(_airbyte_data), 'HKD@spéçiäl & characters') as "HKD@spéçiäl & characters",
    JSONExtractRaw(assumeNotNull(_airbyte_data), 'HKD_special___characters') as HKD_special___characters,
    JSONExtractRaw(assumeNotNull(_airbyte_data), 'NZD') as NZD,
    JSONExtractRaw(assumeNotNull(_airbyte_data), 'USD') as USD,
    _airbyte_ab_id,
    _airbyte_emitted_at,
    now() as _airbyte_normalized_at
from test_normalization._airbyte_raw_dedup_exchange_rate as table_alias
-- dedup_exchange_rate
where 1 = 1

  )