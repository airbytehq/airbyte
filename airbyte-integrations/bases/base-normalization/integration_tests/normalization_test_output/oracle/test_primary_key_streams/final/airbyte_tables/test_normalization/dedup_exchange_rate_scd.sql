

  create  table test_normalization.dedup_exchange_rate_scd__dbt_tmp
  
  as
    
with dbt__cte__dedup_exchange_rate_ab1__ as (

-- SQL model to parse JSON blob stored in a single column and extract into separated field columns as described by the JSON Schema
select
    json_value(airbyte_data, '$."id"') as id,
    json_value(airbyte_data, '$."currency"') as currency,
    json_value(airbyte_data, '$."date"') as "DATE",
    json_value(airbyte_data, '$."timestamp_col"') as timestamp_col,
    json_value(airbyte_data, '$."HKD@spéçiäl & characters"') as hkd_special___characters,
    json_value(airbyte_data, '$."HKD_special___characters"') as hkd_special___characters_1,
    json_value(airbyte_data, '$."NZD"') as nzd,
    json_value(airbyte_data, '$."USD"') as usd,
    airbyte_emitted_at
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
    airbyte_emitted_at
from dbt__cte__dedup_exchange_rate_ab1__
-- dedup_exchange_rate
),  dbt__cte__dedup_exchange_rate_ab3__ as (

-- SQL model to build a hash column based on the values of this record
select
    ora_hash(
        'id' || '~' ||
        'currency' || '~' ||
        "DATE" || '~' ||
        'timestamp_col' || '~' ||
        'hkd_special___characters' || '~' ||
        'hkd_special___characters_1' || '~' ||
        'nzd' || '~' ||
        'usd'
    ) as "_AIRBYTE_DEDUP_EXCHANGE_RATE_HASHID",
    tmp.*
from dbt__cte__dedup_exchange_rate_ab2__ tmp
-- dedup_exchange_rate
),  dbt__cte__dedup_exchange_rate_ab4__ as (

-- SQL model to prepare for deduplicating records based on the hash record column
select
  row_number() over (
    partition by "_AIRBYTE_DEDUP_EXCHANGE_RATE_HASHID"
    order by airbyte_emitted_at asc
  ) as airbyte_row_num,
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
    "DATE" as airbyte_start_at,
    lag("DATE") over (
        partition by id, currency, cast(nzd as varchar2(4000))
        order by "DATE" desc, airbyte_emitted_at desc
    ) as airbyte_end_at,
    coalesce(cast(lag("DATE") over (
        partition by id, currency, cast(nzd as varchar2(4000))
        order by "DATE" desc, airbyte_emitted_at desc
    ) as varchar(200)), 'Latest') as airbyte_active_row,
    airbyte_emitted_at,
    "_AIRBYTE_DEDUP_EXCHANGE_RATE_HASHID"
from dbt__cte__dedup_exchange_rate_ab4__
-- dedup_exchange_rate from test_normalization.airbyte_raw_dedup_exchange_rate
where airbyte_row_num = 1