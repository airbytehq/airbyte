

  create view _airbyte_test_normalization.exchange_rate_ab1__dbt_tmp 
  
  as (
    
-- SQL model to parse JSON blob stored in a single column and extract into separated field columns as described by the JSON Schema
select
    JSONExtractRaw(_airbyte_data, 'id') as id,
    JSONExtractRaw(_airbyte_data, 'currency') as currency,
    JSONExtractRaw(_airbyte_data, 'date') as date,
    JSONExtractRaw(_airbyte_data, 'timestamp_col') as timestamp_col,
    JSONExtractRaw(_airbyte_data, 'HKD@spéçiäl & characters') as "HKD@spéçiäl & characters",
    JSONExtractRaw(_airbyte_data, 'HKD_special___characters') as HKD_special___characters,
    JSONExtractRaw(_airbyte_data, 'NZD') as NZD,
    JSONExtractRaw(_airbyte_data, 'USD') as USD,
    _airbyte_ab_id,
    _airbyte_emitted_at,
    now() as _airbyte_normalized_at
from test_normalization._airbyte_raw_exchange_rate as table_alias
-- exchange_rate
where 1 = 1

  )