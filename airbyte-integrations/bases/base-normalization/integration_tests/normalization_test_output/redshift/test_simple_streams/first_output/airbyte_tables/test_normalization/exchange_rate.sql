

  create  table
    "integrationtests".test_normalization."exchange_rate__dbt_tmp"
    
    
      compound sortkey(_airbyte_emitted_at)
  as (
    
with __dbt__cte__exchange_rate_ab1 as (

-- SQL model to parse JSON blob stored in a single column and extract into separated field columns as described by the JSON Schema
-- depends_on: "integrationtests".test_normalization._airbyte_raw_exchange_rate
select
    case when json_extract_path_text(_airbyte_data, 'id', true) != '' then json_extract_path_text(_airbyte_data, 'id', true) end as id,
    case when json_extract_path_text(_airbyte_data, 'currency', true) != '' then json_extract_path_text(_airbyte_data, 'currency', true) end as currency,
    case when json_extract_path_text(_airbyte_data, 'date', true) != '' then json_extract_path_text(_airbyte_data, 'date', true) end as date,
    case when json_extract_path_text(_airbyte_data, 'timestamp_col', true) != '' then json_extract_path_text(_airbyte_data, 'timestamp_col', true) end as timestamp_col,
    case when json_extract_path_text(_airbyte_data, 'HKD@spéçiäl & characters', true) != '' then json_extract_path_text(_airbyte_data, 'HKD@spéçiäl & characters', true) end as "hkd@spéçiäl & characters",
    case when json_extract_path_text(_airbyte_data, 'HKD_special___characters', true) != '' then json_extract_path_text(_airbyte_data, 'HKD_special___characters', true) end as hkd_special___characters,
    case when json_extract_path_text(_airbyte_data, 'NZD', true) != '' then json_extract_path_text(_airbyte_data, 'NZD', true) end as nzd,
    case when json_extract_path_text(_airbyte_data, 'USD', true) != '' then json_extract_path_text(_airbyte_data, 'USD', true) end as usd,
    case when json_extract_path_text(_airbyte_data, 'column`_''with"_quotes', true) != '' then json_extract_path_text(_airbyte_data, 'column`_''with"_quotes', true) end as "column`_'with""_quotes",
    _airbyte_ab_id,
    _airbyte_emitted_at,
    getdate() as _airbyte_normalized_at
from "integrationtests".test_normalization._airbyte_raw_exchange_rate as table_alias
-- exchange_rate
where 1 = 1
),  __dbt__cte__exchange_rate_ab2 as (

-- SQL model to cast each column to its adequate SQL type converted from the JSON schema type
-- depends_on: __dbt__cte__exchange_rate_ab1
select
    cast(id as 
    bigint
) as id,
    cast(currency as varchar) as currency,
    cast(nullif(date, '') as 
    date
) as date,
    cast(nullif(timestamp_col, '') as 
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
    cast("column`_'with""_quotes" as varchar) as "column`_'with""_quotes",
    _airbyte_ab_id,
    _airbyte_emitted_at,
    getdate() as _airbyte_normalized_at
from __dbt__cte__exchange_rate_ab1
-- exchange_rate
where 1 = 1
),  __dbt__cte__exchange_rate_ab3 as (

-- SQL model to build a hash column based on the values of this record
-- depends_on: __dbt__cte__exchange_rate_ab2
select
    md5(cast(coalesce(cast(id as varchar), '') || '-' || coalesce(cast(currency as varchar), '') || '-' || coalesce(cast(date as varchar), '') || '-' || coalesce(cast(timestamp_col as varchar), '') || '-' || coalesce(cast("hkd@spéçiäl & characters" as varchar), '') || '-' || coalesce(cast(hkd_special___characters as varchar), '') || '-' || coalesce(cast(nzd as varchar), '') || '-' || coalesce(cast(usd as varchar), '') || '-' || coalesce(cast("column`_'with""_quotes" as varchar), '') as varchar)) as _airbyte_exchange_rate_hashid,
    tmp.*
from __dbt__cte__exchange_rate_ab2 tmp
-- exchange_rate
where 1 = 1
)-- Final base SQL model
-- depends_on: __dbt__cte__exchange_rate_ab3
select
    id,
    currency,
    date,
    timestamp_col,
    "hkd@spéçiäl & characters",
    hkd_special___characters,
    nzd,
    usd,
    "column`_'with""_quotes",
    _airbyte_ab_id,
    _airbyte_emitted_at,
    getdate() as _airbyte_normalized_at,
    _airbyte_exchange_rate_hashid
from __dbt__cte__exchange_rate_ab3
-- exchange_rate from "integrationtests".test_normalization._airbyte_raw_exchange_rate
where 1 = 1
  );