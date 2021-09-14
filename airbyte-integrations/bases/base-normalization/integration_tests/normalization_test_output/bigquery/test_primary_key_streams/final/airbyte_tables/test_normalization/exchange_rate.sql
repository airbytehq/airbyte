

  create or replace table `dataline-integration-testing`.test_normalization.`exchange_rate`
  
  
  OPTIONS()
  as (
    
with __dbt__CTE__exchange_rate_ab1 as (

-- SQL model to parse JSON blob stored in a single column and extract into separated field columns as described by the JSON Schema
select
    json_extract_scalar(_airbyte_data, "$['id']") as id,
    json_extract_scalar(_airbyte_data, "$['currency']") as currency,
    json_extract_scalar(_airbyte_data, "$['date']") as date,
    json_extract_scalar(_airbyte_data, "$['timestamp_col']") as timestamp_col,
    json_extract_scalar(_airbyte_data, "$['HKD@spéçiäl & characters']") as HKD_special___characters,
    json_extract_scalar(_airbyte_data, "$['HKD_special___characters']") as HKD_special___characters_1,
    json_extract_scalar(_airbyte_data, "$['NZD']") as NZD,
    json_extract_scalar(_airbyte_data, "$['USD']") as USD,
    _airbyte_emitted_at
from `dataline-integration-testing`.test_normalization._airbyte_raw_exchange_rate as table_alias
-- exchange_rate
),  __dbt__CTE__exchange_rate_ab2 as (

-- SQL model to cast each column to its adequate SQL type converted from the JSON schema type
select
    cast(id as 
    int64
) as id,
    cast(currency as 
    string
) as currency,
    cast(date as 
    date
) as date,
    cast(timestamp_col as 
    timestamp
) as timestamp_col,
    cast(HKD_special___characters as 
    float64
) as HKD_special___characters,
    cast(HKD_special___characters_1 as 
    string
) as HKD_special___characters_1,
    cast(NZD as 
    float64
) as NZD,
    cast(USD as 
    float64
) as USD,
    _airbyte_emitted_at
from __dbt__CTE__exchange_rate_ab1
-- exchange_rate
),  __dbt__CTE__exchange_rate_ab3 as (

-- SQL model to build a hash column based on the values of this record
select
    to_hex(md5(cast(concat(coalesce(cast(id as 
    string
), ''), '-', coalesce(cast(currency as 
    string
), ''), '-', coalesce(cast(date as 
    string
), ''), '-', coalesce(cast(timestamp_col as 
    string
), ''), '-', coalesce(cast(HKD_special___characters as 
    string
), ''), '-', coalesce(cast(HKD_special___characters_1 as 
    string
), ''), '-', coalesce(cast(NZD as 
    string
), ''), '-', coalesce(cast(USD as 
    string
), '')) as 
    string
))) as _airbyte_exchange_rate_hashid,
    tmp.*
from __dbt__CTE__exchange_rate_ab2 tmp
-- exchange_rate
)-- Final base SQL model
select
    id,
    currency,
    date,
    timestamp_col,
    HKD_special___characters,
    HKD_special___characters_1,
    NZD,
    USD,
    _airbyte_emitted_at,
    _airbyte_exchange_rate_hashid
from __dbt__CTE__exchange_rate_ab3
-- exchange_rate from `dataline-integration-testing`.test_normalization._airbyte_raw_exchange_rate
  );
    