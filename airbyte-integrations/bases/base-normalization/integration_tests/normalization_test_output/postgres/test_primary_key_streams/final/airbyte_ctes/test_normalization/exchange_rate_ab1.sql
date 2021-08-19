
  create view "postgres"._airbyte_test_normalization."exchange_rate_ab1__dbt_tmp" as (
    
-- SQL model to parse JSON blob stored in a single column and extract into separated field columns as described by the JSON Schema
select
    jsonb_extract_path_text(_airbyte_data, 'id') as "id",
    jsonb_extract_path_text(_airbyte_data, 'currency') as currency,
    jsonb_extract_path_text(_airbyte_data, 'date') as "date",
    jsonb_extract_path_text(_airbyte_data, 'timestamp_col') as timestamp_col,
    jsonb_extract_path_text(_airbyte_data, 'HKD@spéçiäl & characters') as "HKD@spéçiäl & characters",
    jsonb_extract_path_text(_airbyte_data, 'HKD_special___characters') as hkd_special___characters,
    jsonb_extract_path_text(_airbyte_data, 'NZD') as nzd,
    jsonb_extract_path_text(_airbyte_data, 'USD') as usd,
    _airbyte_emitted_at
from "postgres".test_normalization._airbyte_raw_exchange_rate as table_alias
-- exchange_rate
  );
