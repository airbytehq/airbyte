

  create  table
    test_normalization.`exchange_rate__dbt_tmp`
  as (
    
with __dbt__CTE__exchange_rate_ab1 as (

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
),  __dbt__CTE__exchange_rate_ab2 as (

-- SQL model to cast each column to its adequate SQL type converted from the JSON schema type
select
    cast(id as 
    signed
) as id,
    cast(currency as char) as currency,
    cast(`date` as 
    date
) as `date`,
    cast(timestamp_col as char) as timestamp_col,
    cast(`HKD@spéçiäl & characters` as 
    float
) as `HKD@spéçiäl & characters`,
    cast(hkd_special___characters as char) as hkd_special___characters,
    cast(nzd as 
    float
) as nzd,
    cast(usd as 
    float
) as usd,
    _airbyte_emitted_at
from __dbt__CTE__exchange_rate_ab1
-- exchange_rate
),  __dbt__CTE__exchange_rate_ab3 as (

-- SQL model to build a hash column based on the values of this record
select
    md5(cast(concat(coalesce(cast(id as char), ''), '-', coalesce(cast(currency as char), ''), '-', coalesce(cast(`date` as char), ''), '-', coalesce(cast(timestamp_col as char), ''), '-', coalesce(cast(`HKD@spéçiäl & characters` as char), ''), '-', coalesce(cast(hkd_special___characters as char), ''), '-', coalesce(cast(nzd as char), ''), '-', coalesce(cast(usd as char), '')) as char)) as _airbyte_exchange_rate_hashid,
    tmp.*
from __dbt__CTE__exchange_rate_ab2 tmp
-- exchange_rate
)-- Final base SQL model
select
    id,
    currency,
    `date`,
    timestamp_col,
    `HKD@spéçiäl & characters`,
    hkd_special___characters,
    nzd,
    usd,
    _airbyte_emitted_at,
    _airbyte_exchange_rate_hashid
from __dbt__CTE__exchange_rate_ab3
-- exchange_rate from test_normalization._airbyte_raw_exchange_rate
  )
