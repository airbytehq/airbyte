

  create  table test_normalization.exchange_rate__dbt_tmp
  
  as
    
with dbt__cte__exchange_rate_ab1__ as (

-- SQL model to parse JSON blob stored in a single column and extract into separated field columns as described by the JSON Schema
-- depends_on: test_normalization.airbyte_raw_exchange_rate
select
    json_value("_AIRBYTE_DATA", '$."id"') as id,
    json_value("_AIRBYTE_DATA", '$."currency"') as currency,
    json_value("_AIRBYTE_DATA", '$."date"') as "DATE",
    json_value("_AIRBYTE_DATA", '$."timestamp_col"') as timestamp_col,
    json_value("_AIRBYTE_DATA", '$."HKD@spéçiäl & characters"') as hkd_special___characters,
    json_value("_AIRBYTE_DATA", '$."HKD_special___characters"') as hkd_special___characters_1,
    json_value("_AIRBYTE_DATA", '$."NZD"') as nzd,
    json_value("_AIRBYTE_DATA", '$."USD"') as usd,
    json_value("_AIRBYTE_DATA", '$."column___with__quotes"') as column___with__quotes,
    json_value("_AIRBYTE_DATA", '$."datetime_tz"') as datetime_tz,
    json_value("_AIRBYTE_DATA", '$."datetime_no_tz"') as datetime_no_tz,
    json_value("_AIRBYTE_DATA", '$."time_tz"') as time_tz,
    json_value("_AIRBYTE_DATA", '$."time_no_tz"') as time_no_tz,
    json_value("_AIRBYTE_DATA", '$."property_binary_data"') as property_binary_data,
    "_AIRBYTE_AB_ID",
    "_AIRBYTE_EMITTED_AT",
    
    CURRENT_TIMESTAMP
 as "_AIRBYTE_NORMALIZED_AT"
from test_normalization.airbyte_raw_exchange_rate 
-- exchange_rate
where 1 = 1
),  dbt__cte__exchange_rate_ab2__ as (

-- SQL model to cast each column to its adequate SQL type converted from the JSON schema type
-- depends_on: dbt__cte__exchange_rate_ab1__
select
    cast(id as 
    numeric
) as id,
    cast(currency as varchar2(4000)) as currency,
    cast(nullif("DATE", '') as 
    varchar2(4000)
) as "DATE",
    cast(nullif(timestamp_col, '') as 
    varchar2(4000)
) as timestamp_col,
    cast(hkd_special___characters as 
    float
) as hkd_special___characters,
    cast(hkd_special___characters_1 as varchar2(4000)) as hkd_special___characters_1,
    cast(nzd as 
    float
) as nzd,
    cast(usd as 
    float
) as usd,
    cast(column___with__quotes as varchar2(4000)) as column___with__quotes,
    cast(nullif(datetime_tz, '') as 
    varchar2(4000)
) as datetime_tz,
    cast(nullif(datetime_no_tz, '') as 
    varchar2(4000)
) as datetime_no_tz,
    cast(nullif(time_tz, '') as 
    varchar2(4000)
) as time_tz,
    cast(nullif(time_no_tz, '') as 
    varchar2(4000)
) as time_no_tz,
    cast(property_binary_data as varchar2(4000)) as property_binary_data,
    "_AIRBYTE_AB_ID",
    "_AIRBYTE_EMITTED_AT",
    
    CURRENT_TIMESTAMP
 as "_AIRBYTE_NORMALIZED_AT"
from dbt__cte__exchange_rate_ab1__
-- exchange_rate
where 1 = 1
),  dbt__cte__exchange_rate_ab3__ as (

-- SQL model to build a hash column based on the values of this record
-- depends_on: dbt__cte__exchange_rate_ab2__
select
    ora_hash(
            
                id || '~' ||
            
            
                currency || '~' ||
            
            
                "DATE" || '~' ||
            
            
                timestamp_col || '~' ||
            
            
                hkd_special___characters || '~' ||
            
            
                hkd_special___characters_1 || '~' ||
            
            
                nzd || '~' ||
            
            
                usd || '~' ||
            
            
                column___with__quotes || '~' ||
            
            
                datetime_tz || '~' ||
            
            
                datetime_no_tz || '~' ||
            
            
                time_tz || '~' ||
            
            
                time_no_tz || '~' ||
            
            
                property_binary_data
            
    ) as "_AIRBYTE_EXCHANGE_RATE_HASHID",
    tmp.*
from dbt__cte__exchange_rate_ab2__ tmp
-- exchange_rate
where 1 = 1
)-- Final base SQL model
-- depends_on: dbt__cte__exchange_rate_ab3__
select
    id,
    currency,
    "DATE",
    timestamp_col,
    hkd_special___characters,
    hkd_special___characters_1,
    nzd,
    usd,
    column___with__quotes,
    datetime_tz,
    datetime_no_tz,
    time_tz,
    time_no_tz,
    property_binary_data,
    "_AIRBYTE_AB_ID",
    "_AIRBYTE_EMITTED_AT",
    
    CURRENT_TIMESTAMP
 as "_AIRBYTE_NORMALIZED_AT",
    "_AIRBYTE_EXCHANGE_RATE_HASHID"
from dbt__cte__exchange_rate_ab3__
-- exchange_rate from test_normalization.airbyte_raw_exchange_rate
where 1 = 1