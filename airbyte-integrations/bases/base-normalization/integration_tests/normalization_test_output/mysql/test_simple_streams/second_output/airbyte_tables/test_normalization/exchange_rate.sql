

  create  table
    test_normalization.`exchange_rate__dbt_tmp`
  as (
    
with __dbt__cte__exchange_rate_ab1 as (

-- SQL model to parse JSON blob stored in a single column and extract into separated field columns as described by the JSON Schema
-- depends_on: test_normalization._airbyte_raw_exchange_rate
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
    json_value(_airbyte_data, 
    '$."column___with__quotes"' RETURNING CHAR) as `column__'with"_quotes`,
    json_value(_airbyte_data, 
    '$."datetime_tz"' RETURNING CHAR) as datetime_tz,
    json_value(_airbyte_data, 
    '$."datetime_no_tz"' RETURNING CHAR) as datetime_no_tz,
    json_value(_airbyte_data, 
    '$."time_tz"' RETURNING CHAR) as time_tz,
    json_value(_airbyte_data, 
    '$."time_no_tz"' RETURNING CHAR) as time_no_tz,
    json_value(_airbyte_data, 
    '$."property_binary_data"' RETURNING CHAR) as property_binary_data,
    _airbyte_ab_id,
    _airbyte_emitted_at,
    
    CURRENT_TIMESTAMP
 as _airbyte_normalized_at
from test_normalization._airbyte_raw_exchange_rate as table_alias
-- exchange_rate
where 1 = 1
),  __dbt__cte__exchange_rate_ab2 as (

-- SQL model to cast each column to its adequate SQL type converted from the JSON schema type
-- depends_on: __dbt__cte__exchange_rate_ab1
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
    cast(`column__'with"_quotes` as char(1024)) as `column__'with"_quotes`,
    cast(nullif(datetime_tz, '') as char(1024)) as datetime_tz,
        case when datetime_no_tz regexp '\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}.*' THEN STR_TO_DATE(SUBSTR(datetime_no_tz, 1, 19), '%Y-%m-%dT%H:%i:%S')
        else cast(if(datetime_no_tz = '', NULL, datetime_no_tz) as datetime)
        end as datetime_no_tz
        ,
    nullif(cast(time_tz as char(1024)), "") as time_tz,
    nullif(cast(time_no_tz as 
    time
), "") as time_no_tz,
    cast(FROM_BASE64(property_binary_data) as binary) as property_binary_data,
    _airbyte_ab_id,
    _airbyte_emitted_at,
    
    CURRENT_TIMESTAMP
 as _airbyte_normalized_at
from __dbt__cte__exchange_rate_ab1
-- exchange_rate
where 1 = 1
),  __dbt__cte__exchange_rate_ab3 as (

-- SQL model to build a hash column based on the values of this record
-- depends_on: __dbt__cte__exchange_rate_ab2
select
    md5(cast(concat(coalesce(cast(id as char), ''), '-', coalesce(cast(currency as char), ''), '-', coalesce(cast(`date` as char), ''), '-', coalesce(cast(timestamp_col as char), ''), '-', coalesce(cast(`HKD@spéçiäl & characters` as char), ''), '-', coalesce(cast(hkd_special___characters as char), ''), '-', coalesce(cast(nzd as char), ''), '-', coalesce(cast(usd as char), ''), '-', coalesce(cast(`column__'with"_quotes` as char), ''), '-', coalesce(cast(datetime_tz as char), ''), '-', coalesce(cast(datetime_no_tz as char), ''), '-', coalesce(cast(time_tz as char), ''), '-', coalesce(cast(time_no_tz as char), ''), '-', coalesce(cast(property_binary_data as char), '')) as char)) as _airbyte_exchange_rate_hashid,
    tmp.*
from __dbt__cte__exchange_rate_ab2 tmp
-- exchange_rate
where 1 = 1
)-- Final base SQL model
-- depends_on: __dbt__cte__exchange_rate_ab3
select
    id,
    currency,
    `date`,
    timestamp_col,
    `HKD@spéçiäl & characters`,
    hkd_special___characters,
    nzd,
    usd,
    `column__'with"_quotes`,
    datetime_tz,
    datetime_no_tz,
    time_tz,
    time_no_tz,
    property_binary_data,
    _airbyte_ab_id,
    _airbyte_emitted_at,
    
    CURRENT_TIMESTAMP
 as _airbyte_normalized_at,
    _airbyte_exchange_rate_hashid
from __dbt__cte__exchange_rate_ab3
-- exchange_rate from test_normalization._airbyte_raw_exchange_rate
where 1 = 1
  )
