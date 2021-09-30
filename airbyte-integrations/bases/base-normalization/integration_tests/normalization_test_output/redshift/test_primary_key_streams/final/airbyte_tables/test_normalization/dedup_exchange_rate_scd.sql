

  create  table
    "integrationtests".test_normalization."dedup_exchange_rate_scd__dbt_tmp"
    
    
  as (
    
with __dbt__CTE__dedup_exchange_rate_ab1 as (

-- SQL model to parse JSON blob stored in a single column and extract into separated field columns as described by the JSON Schema
select
    case when json_extract_path_text(_airbyte_data, 'id', true) != '' then json_extract_path_text(_airbyte_data, 'id', true) end as id,
    case when json_extract_path_text(_airbyte_data, 'currency', true) != '' then json_extract_path_text(_airbyte_data, 'currency', true) end as currency,
    case when json_extract_path_text(_airbyte_data, 'date', true) != '' then json_extract_path_text(_airbyte_data, 'date', true) end as date,
    case when json_extract_path_text(_airbyte_data, 'timestamp_col', true) != '' then json_extract_path_text(_airbyte_data, 'timestamp_col', true) end as timestamp_col,
    case when json_extract_path_text(_airbyte_data, 'HKD@spéçiäl & characters', true) != '' then json_extract_path_text(_airbyte_data, 'HKD@spéçiäl & characters', true) end as "hkd@spéçiäl & characters",
    case when json_extract_path_text(_airbyte_data, 'HKD_special___characters', true) != '' then json_extract_path_text(_airbyte_data, 'HKD_special___characters', true) end as hkd_special___characters,
    case when json_extract_path_text(_airbyte_data, 'NZD', true) != '' then json_extract_path_text(_airbyte_data, 'NZD', true) end as nzd,
    case when json_extract_path_text(_airbyte_data, 'USD', true) != '' then json_extract_path_text(_airbyte_data, 'USD', true) end as usd,
    _airbyte_emitted_at
from "integrationtests".test_normalization._airbyte_raw_dedup_exchange_rate as table_alias
-- dedup_exchange_rate
),  __dbt__CTE__dedup_exchange_rate_ab2 as (

-- SQL model to cast each column to its adequate SQL type converted from the JSON schema type
select
    cast(id as 
    bigint
) as id,
    cast(currency as varchar) as currency,
    cast(date as 
    date
) as date,
    cast(timestamp_col as 
    timestamp with time zone
) as timestamp_col,
    cast("hkd@spéçiäl & characters" as 
    float
) as "hkd@spéçiäl & characters",
    cast(hkd_special___characters as varchar) as hkd_special___characters,
    cast(nzd as 
    float
) as nzd,
    cast(usd as 
    float
) as usd,
    _airbyte_emitted_at
from __dbt__CTE__dedup_exchange_rate_ab1
-- dedup_exchange_rate
),  __dbt__CTE__dedup_exchange_rate_ab3 as (

-- SQL model to build a hash column based on the values of this record
select
    md5(cast(
    
    coalesce(cast(id as varchar), '') || '-' || coalesce(cast(currency as varchar), '') || '-' || coalesce(cast(date as varchar), '') || '-' || coalesce(cast(timestamp_col as varchar), '') || '-' || coalesce(cast("hkd@spéçiäl & characters" as varchar), '') || '-' || coalesce(cast(hkd_special___characters as varchar), '') || '-' || coalesce(cast(nzd as varchar), '') || '-' || coalesce(cast(usd as varchar), '')

 as varchar)) as _airbyte_dedup_exchange_rate_hashid,
    tmp.*
from __dbt__CTE__dedup_exchange_rate_ab2 tmp
-- dedup_exchange_rate
),  __dbt__CTE__dedup_exchange_rate_ab4 as (

-- SQL model to prepare for deduplicating records based on the hash record column
select
  row_number() over (
    partition by _airbyte_dedup_exchange_rate_hashid
    order by _airbyte_emitted_at asc
  ) as _airbyte_row_num,
  tmp.*
from __dbt__CTE__dedup_exchange_rate_ab3 tmp
-- dedup_exchange_rate from "integrationtests".test_normalization._airbyte_raw_dedup_exchange_rate
)-- SQL model to build a Type 2 Slowly Changing Dimension (SCD) table for each record identified by their primary key
select
    id,
    currency,
    date,
    timestamp_col,
    "hkd@spéçiäl & characters",
    hkd_special___characters,
    nzd,
    usd,
  date as _airbyte_start_at,
  lag(date) over (
    partition by id, currency, cast(nzd as varchar)
    order by date is null asc, date desc, _airbyte_emitted_at desc
  ) as _airbyte_end_at,
  case when lag(date) over (
    partition by id, currency, cast(nzd as varchar)
    order by date is null asc, date desc, _airbyte_emitted_at desc
  ) is null  then 1 else 0 end as _airbyte_active_row,
  _airbyte_emitted_at,
  _airbyte_dedup_exchange_rate_hashid
from __dbt__CTE__dedup_exchange_rate_ab4
-- dedup_exchange_rate from "integrationtests".test_normalization._airbyte_raw_dedup_exchange_rate
where _airbyte_row_num = 1
  );