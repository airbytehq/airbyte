

  create view "integrationtests"._airbyte_test_normalization."_airbyte_test_normalization_dedup_exchange_rate_ab1__dbt_tmp" as (
    
-- SQL model to parse JSON blob stored in a single column and extract into separated field columns as described by the JSON Schema
select
    case when json_extract_path_text(_airbyte_data, 'id') != '' then json_extract_path_text(_airbyte_data, 'id') end as id,
    case when json_extract_path_text(_airbyte_data, 'currency') != '' then json_extract_path_text(_airbyte_data, 'currency') end as currency,
    case when json_extract_path_text(_airbyte_data, 'date') != '' then json_extract_path_text(_airbyte_data, 'date') end as date,
    case when json_extract_path_text(_airbyte_data, 'HKD') != '' then json_extract_path_text(_airbyte_data, 'HKD') end as hkd,
    case when json_extract_path_text(_airbyte_data, 'NZD') != '' then json_extract_path_text(_airbyte_data, 'NZD') end as nzd,
    case when json_extract_path_text(_airbyte_data, 'USD') != '' then json_extract_path_text(_airbyte_data, 'USD') end as usd,
    _airbyte_emitted_at
from "integrationtests".test_normalization._airbyte_raw_dedup_exchange_rate
-- dedup_exchange_rate
  ) ;
