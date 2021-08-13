
  create view _airbyte_test_normalization.`exchange_rate_ab1__dbt_tmp` as (
    
-- SQL model to parse JSON blob stored in a single column and extract into separated field columns as described by the JSON Schema
select
    json_value(_airbyte_data, 
    '$."id"') as id,
    json_value(_airbyte_data, 
    '$."currency"') as currency,
    json_value(_airbyte_data, 
    '$."date"') as `date`,
    json_value(_airbyte_data, 
    '$."timestamp_col"') as timestamp_col,
    json_value(_airbyte_data, 
    '$."HKD@spéçiäl & characters"') as `HKD@spéçiäl & characters`,
    json_value(_airbyte_data, 
    '$."HKD_special___characters"') as hkd_special___characters,
    json_value(_airbyte_data, 
    '$."NZD"') as nzd,
    json_value(_airbyte_data, 
    '$."USD"') as usd,
    _airbyte_emitted_at
from test_normalization._airbyte_raw_exchange_rate as table_alias
-- exchange_rate
  );
