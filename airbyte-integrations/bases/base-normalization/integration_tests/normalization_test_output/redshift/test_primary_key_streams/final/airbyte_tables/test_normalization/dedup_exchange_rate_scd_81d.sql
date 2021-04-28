

  create  table
    "integrationtests".test_normalization."dedup_exchange_rate_scd_81d__dbt_tmp"
    
    
  as (
    
with __dbt__CTE__dedup_exchange_rate_ab1_281 as (

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
),  __dbt__CTE__dedup_exchange_rate_ab2_281 as (

-- SQL model to cast each column to its adequate SQL type converted from the JSON schema type
select
    cast(id as 
    bigint
) as id,
    cast(currency as varchar) as currency,
    cast(date as varchar) as date,
    cast(hkd as 
    float
) as hkd,
    cast(nzd as 
    float
) as nzd,
    cast(usd as 
    float
) as usd,
    _airbyte_emitted_at
from __dbt__CTE__dedup_exchange_rate_ab1_281
-- dedup_exchange_rate
),  __dbt__CTE__dedup_exchange_rate_ab3_281 as (

-- SQL model to build a hash column based on the values of this record
select
    *,
    md5(cast(
    
    coalesce(cast(id as varchar), '') || '-' || coalesce(cast(currency as varchar), '') || '-' || coalesce(cast(date as varchar), '') || '-' || coalesce(cast(hkd as varchar), '') || '-' || coalesce(cast(nzd as varchar), '') || '-' || coalesce(cast(usd as varchar), '')

 as varchar)) as _airbyte_dedup_exchange_rate_hashid
from __dbt__CTE__dedup_exchange_rate_ab2_281
-- dedup_exchange_rate
),  __dbt__CTE__dedup_exchange_rate_ab4_281 as (

-- SQL model to prepare for deduplicating records based on the hash record column
select
  *,
  row_number() over (
    partition by _airbyte_dedup_exchange_rate_hashid
    order by _airbyte_emitted_at asc
  ) as _airbyte_row_num
from __dbt__CTE__dedup_exchange_rate_ab3_281
-- dedup_exchange_rate from "integrationtests".test_normalization._airbyte_raw_dedup_exchange_rate
)-- SQL model to build a Type 2 Slowly Changing Dimension (SCD) table for each record identified by their primary key
select
    id,
    currency,
    date,
    hkd,
    nzd,
    usd,
    date as _airbyte_start_at,
    lag(date) over (
        partition by id, currency, cast(nzd as varchar)
        order by date desc, _airbyte_emitted_at desc
    ) as _airbyte_end_at,
    lag(date) over (
        partition by id, currency, cast(nzd as varchar)
        order by date desc, _airbyte_emitted_at desc
    ) is null as _airbyte_active_row,
    _airbyte_emitted_at,
    _airbyte_dedup_exchange_rate_hashid
from __dbt__CTE__dedup_exchange_rate_ab4_281
-- dedup_exchange_rate from "integrationtests".test_normalization._airbyte_raw_dedup_exchange_rate
where _airbyte_row_num = 1
  );