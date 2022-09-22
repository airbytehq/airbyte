
  create view _airbyte_test_normalization.`dedup_exchange_rate_stg__dbt_tmp` as (
    
with __dbt__cte__dedup_exchange_rate_ab1 as (

-- SQL model to parse JSON blob stored in a single column and extract into separated field columns as described by the JSON Schema
-- depends_on: test_normalization._airbyte_raw_dedup_exchange_rate
select
    json_value(_airbyte_data, 
    '$."id"' RETURNING CHAR) as id,
    json_value(_airbyte_data, 
    '$."currency"' RETURNING CHAR) as currency,
    json_value(_airbyte_data, 
    '$."date"' RETURNING CHAR) as `date`,
    json_value(_airbyte_data, 
    '$."timestamp_col"' RETURNING CHAR) as timestamp_col,
    json_value(_airbyte_data, 
    '$."HKD@spéçiäl & characters"' RETURNING CHAR) as `HKD@spéçiäl & characters`,
    json_value(_airbyte_data, 
    '$."HKD_special___characters"' RETURNING CHAR) as hkd_special___characters,
    json_value(_airbyte_data, 
    '$."NZD"' RETURNING CHAR) as nzd,
    json_value(_airbyte_data, 
    '$."USD"' RETURNING CHAR) as usd,
    _airbyte_ab_id,
    _airbyte_emitted_at,
    
    CURRENT_TIMESTAMP
 as _airbyte_normalized_at
from test_normalization._airbyte_raw_dedup_exchange_rate as table_alias
-- dedup_exchange_rate
where 1 = 1

),  __dbt__cte__dedup_exchange_rate_ab2 as (

-- SQL model to cast each column to its adequate SQL type converted from the JSON schema type
-- depends_on: __dbt__cte__dedup_exchange_rate_ab1
select
    cast(id as 
    signed
) as id,
    cast(currency as char(1024)) as currency,
        case when `date` = '' then NULL
        else cast(`date` as date)
        end as `date`
        ,
    cast(nullif(timestamp_col, '') as char(1024)) as timestamp_col,
    cast(`HKD@spéçiäl & characters` as 
    float
) as `HKD@spéçiäl & characters`,
    cast(hkd_special___characters as char(1024)) as hkd_special___characters,
    cast(nzd as 
    float
) as nzd,
    cast(usd as 
    float
) as usd,
    _airbyte_ab_id,
    _airbyte_emitted_at,
    
    CURRENT_TIMESTAMP
 as _airbyte_normalized_at
from __dbt__cte__dedup_exchange_rate_ab1
-- dedup_exchange_rate
where 1 = 1

)-- SQL model to build a hash column based on the values of this record
-- depends_on: __dbt__cte__dedup_exchange_rate_ab2
select
    md5(cast(concat(coalesce(cast(id as char), ''), '-', coalesce(cast(currency as char), ''), '-', coalesce(cast(`date` as char), ''), '-', coalesce(cast(timestamp_col as char), ''), '-', coalesce(cast(`HKD@spéçiäl & characters` as char), ''), '-', coalesce(cast(hkd_special___characters as char), ''), '-', coalesce(cast(nzd as char), ''), '-', coalesce(cast(usd as char), '')) as char)) as _airbyte_dedup_exchange_rate_hashid,
    tmp.*
from __dbt__cte__dedup_exchange_rate_ab2 tmp
-- dedup_exchange_rate
where 1 = 1

  );