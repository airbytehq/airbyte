

  create or replace view `dataline-integration-testing`._airbyte_test_normalization.`exchange_rate_ab1`
  OPTIONS()
  as 
-- SQL model to parse JSON blob stored in a single column and extract into separated field columns as described by the JSON Schema
select
    json_extract_scalar(_airbyte_data, "$['id']") as id,
    json_extract_scalar(_airbyte_data, "$['currency']") as currency,
    json_extract_scalar(_airbyte_data, "$['date']") as date,
    json_extract_scalar(_airbyte_data, "$['HKD@spéçiäl & characters']") as HKD_special___characters,
    json_extract_scalar(_airbyte_data, "$['HKD_special___characters']") as HKD_special___characters_1,
    json_extract_scalar(_airbyte_data, "$['NZD']") as NZD,
    json_extract_scalar(_airbyte_data, "$['USD']") as USD,
    _airbyte_emitted_at
from `dataline-integration-testing`.test_normalization._airbyte_raw_exchange_rate
-- exchange_rate;

