

  create  table test_normalization.dedup_exchange_rate_scd__dbt_tmp
  
  as
    
with dbt__cte__dedup_exchange_rate_ab1__ as (

-- SQL model to parse JSON blob stored in a single column and extract into separated field columns as described by the JSON Schema
select
    json_value("_AIRBYTE_DATA", '$."id"') as id,
    json_value("_AIRBYTE_DATA", '$."currency"') as currency,
    json_value("_AIRBYTE_DATA", '$."date"') as "DATE",
    json_value("_AIRBYTE_DATA", '$."timestamp_col"') as timestamp_col,
    json_value("_AIRBYTE_DATA", '$."HKD@spéçiäl & characters"') as hkd_special___characters,
    json_value("_AIRBYTE_DATA", '$."HKD_special___characters"') as hkd_special___characters_1,
    json_value("_AIRBYTE_DATA", '$."NZD"') as nzd,
    json_value("_AIRBYTE_DATA", '$."USD"') as usd,
    "_AIRBYTE_EMITTED_AT"
from test_normalization.airbyte_raw_dedup_exchange_rate 
-- dedup_exchange_rate
),  dbt__cte__dedup_exchange_rate_ab2__ as (

-- SQL model to cast each column to its adequate SQL type converted from the JSON schema type
select
    cast(id as 
    numeric
) as id,
    cast(currency as varchar2(4000)) as currency,
    cast("DATE" as 
    varchar2(4000)
) as "DATE",
    cast(timestamp_col as 
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
    "_AIRBYTE_EMITTED_AT"
from dbt__cte__dedup_exchange_rate_ab1__
-- dedup_exchange_rate
),  dbt__cte__dedup_exchange_rate_ab3__ as (

-- SQL model to build a hash column based on the values of this record
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
),  dbt__cte__dedup_exchange_rate_ab4__ as (

-- SQL model to prepare for deduplicating records based on the hash record column
select
  row_number() over (
    partition by "_AIRBYTE_DEDUP_EXCHANGE_RATE_HASHID"
    order by "_AIRBYTE_EMITTED_AT" asc
  ) as "_AIRBYTE_ROW_NUM",
  tmp.*
from dbt__cte__dedup_exchange_rate_ab3__ tmp
-- dedup_exchange_rate from test_normalization.airbyte_raw_dedup_exchange_rate
)-- SQL model to build a Type 2 Slowly Changing Dimension (SCD) table for each record identified by their primary key
select
    id,
    currency,
    "DATE",
    timestamp_col,
    hkd_special___characters,
    hkd_special___characters_1,
    nzd,
    usd,
  "DATE" as "_AIRBYTE_START_AT",
  lag("DATE") over (
    partition by id, currency, cast(nzd as varchar2(4000))
    order by "DATE" asc nulls first, "DATE" desc, "_AIRBYTE_EMITTED_AT" desc
  ) as "_AIRBYTE_END_AT",
  case when lag("DATE") over (
    partition by id, currency, cast(nzd as varchar2(4000))
    order by "DATE" asc nulls first, "DATE" desc, "_AIRBYTE_EMITTED_AT" desc
  ) is null  then 1 else 0 end as "_AIRBYTE_ACTIVE_ROW",
  "_AIRBYTE_EMITTED_AT",
  "_AIRBYTE_DEDUP_EXCHANGE_RATE_HASHID"
from dbt__cte__dedup_exchange_rate_ab4__
-- dedup_exchange_rate from test_normalization.airbyte_raw_dedup_exchange_rate
where "_AIRBYTE_ROW_NUM" = 1