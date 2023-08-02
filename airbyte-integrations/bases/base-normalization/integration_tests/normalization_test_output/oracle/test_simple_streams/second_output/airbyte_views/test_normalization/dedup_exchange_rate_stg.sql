
  create view test_normalization.dedup_exchange_rate_stg__dbt_tmp as
    
with dbt__cte__dedup_exchange_rate_ab1__ as (

-- SQL model to parse JSON blob stored in a single column and extract into separated field columns as described by the JSON Schema
-- depends_on: test_normalization.airbyte_raw_dedup_exchange_rate
select
    json_value("_AIRBYTE_DATA", '$."id"') as id,
    json_value("_AIRBYTE_DATA", '$."currency"') as currency,
    json_value("_AIRBYTE_DATA", '$."date"') as "DATE",
    json_value("_AIRBYTE_DATA", '$."timestamp_col"') as timestamp_col,
    json_value("_AIRBYTE_DATA", '$."HKD@spéçiäl & characters"') as hkd_special___characters,
    json_value("_AIRBYTE_DATA", '$."HKD_special___characters"') as hkd_special___characters_1,
    json_value("_AIRBYTE_DATA", '$."NZD"') as nzd,
    json_value("_AIRBYTE_DATA", '$."USD"') as usd,
    "_AIRBYTE_AB_ID",
    "_AIRBYTE_EMITTED_AT",
    
    CURRENT_TIMESTAMP
 as "_AIRBYTE_NORMALIZED_AT"
from test_normalization.airbyte_raw_dedup_exchange_rate 
-- dedup_exchange_rate
where 1 = 1

),  dbt__cte__dedup_exchange_rate_ab2__ as (

-- SQL model to cast each column to its adequate SQL type converted from the JSON schema type
-- depends_on: dbt__cte__dedup_exchange_rate_ab1__
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
    "_AIRBYTE_AB_ID",
    "_AIRBYTE_EMITTED_AT",
    
    CURRENT_TIMESTAMP
 as "_AIRBYTE_NORMALIZED_AT"
from dbt__cte__dedup_exchange_rate_ab1__
-- dedup_exchange_rate
where 1 = 1

)-- SQL model to build a hash column based on the values of this record
-- depends_on: dbt__cte__dedup_exchange_rate_ab2__
select
    ora_hash(
            
                id || '~' ||
            
            
                currency || '~' ||
            
            
                "DATE" || '~' ||
            
            
                timestamp_col || '~' ||
            
            
                hkd_special___characters || '~' ||
            
            
                hkd_special___characters_1 || '~' ||
            
            
                nzd || '~' ||
            
            
                usd
            
    ) as "_AIRBYTE_DEDUP_EXCHANGE_RATE_HASHID",
    tmp.*
from dbt__cte__dedup_exchange_rate_ab2__ tmp
-- dedup_exchange_rate
where 1 = 1


