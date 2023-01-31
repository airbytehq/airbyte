

  create  table "postgres".test_normalization."exchange_rate__dbt_tmp"
  as (
    
with __dbt__cte__exchange_rate_ab1 as (

-- SQL model to parse JSON blob stored in a single column and extract into separated field columns as described by the JSON Schema
-- depends_on: "postgres".test_normalization._airbyte_raw_exchange_rate
select
    jsonb_extract_path_text(_airbyte_data, 'id') as "id",
    jsonb_extract_path_text(_airbyte_data, 'currency') as currency,
    jsonb_extract_path_text(_airbyte_data, 'date') as "date",
    jsonb_extract_path_text(_airbyte_data, 'timestamp_col') as timestamp_col,
    jsonb_extract_path_text(_airbyte_data, 'HKD@spéçiäl & characters') as "HKD@spéçiäl & characters",
    jsonb_extract_path_text(_airbyte_data, 'HKD_special___characters') as hkd_special___characters,
    jsonb_extract_path_text(_airbyte_data, 'NZD') as nzd,
    jsonb_extract_path_text(_airbyte_data, 'USD') as usd,
    jsonb_extract_path_text(_airbyte_data, 'column`_''with"_quotes') as "column`_'with""_quotes",
    jsonb_extract_path_text(_airbyte_data, 'datetime_tz') as datetime_tz,
    jsonb_extract_path_text(_airbyte_data, 'datetime_no_tz') as datetime_no_tz,
    jsonb_extract_path_text(_airbyte_data, 'time_tz') as time_tz,
    jsonb_extract_path_text(_airbyte_data, 'time_no_tz') as time_no_tz,
    jsonb_extract_path_text(_airbyte_data, 'property_binary_data') as property_binary_data,
    _airbyte_ab_id,
    _airbyte_emitted_at,
    now() as _airbyte_normalized_at
from "postgres".test_normalization._airbyte_raw_exchange_rate as table_alias
-- exchange_rate
where 1 = 1
),  __dbt__cte__exchange_rate_ab2 as (

-- SQL model to cast each column to its adequate SQL type converted from the JSON schema type
-- depends_on: __dbt__cte__exchange_rate_ab1
select
    cast("id" as 
    bigint
) as "id",
    cast(currency as text) as currency,
    cast(nullif("date", '') as 
    date
) as "date",
    cast(nullif(timestamp_col, '') as 
    timestamp with time zone
) as timestamp_col,
    cast("HKD@spéçiäl & characters" as 
    float
) as "HKD@spéçiäl & characters",
    cast(hkd_special___characters as text) as hkd_special___characters,
    cast(nzd as 
    float
) as nzd,
    cast(usd as 
    float
) as usd,
    cast("column`_'with""_quotes" as text) as "column`_'with""_quotes",
    cast(nullif(datetime_tz, '') as 
    timestamp with time zone
) as datetime_tz,
    cast(nullif(datetime_no_tz, '') as 
    timestamp
) as datetime_no_tz,
    cast(nullif(time_tz, '') as 
    time with time zone
) as time_tz,
    cast(nullif(time_no_tz, '') as 
    time
) as time_no_tz,
    cast(decode(property_binary_data, 'base64') as bytea) as property_binary_data,
    _airbyte_ab_id,
    _airbyte_emitted_at,
    now() as _airbyte_normalized_at
from __dbt__cte__exchange_rate_ab1
-- exchange_rate
where 1 = 1
),  __dbt__cte__exchange_rate_ab3 as (

-- SQL model to build a hash column based on the values of this record
-- depends_on: __dbt__cte__exchange_rate_ab2
select
    md5(cast(coalesce(cast("id" as text), '') || '-' || coalesce(cast(currency as text), '') || '-' || coalesce(cast("date" as text), '') || '-' || coalesce(cast(timestamp_col as text), '') || '-' || coalesce(cast("HKD@spéçiäl & characters" as text), '') || '-' || coalesce(cast(hkd_special___characters as text), '') || '-' || coalesce(cast(nzd as text), '') || '-' || coalesce(cast(usd as text), '') || '-' || coalesce(cast("column`_'with""_quotes" as text), '') || '-' || coalesce(cast(datetime_tz as text), '') || '-' || coalesce(cast(datetime_no_tz as text), '') || '-' || coalesce(cast(time_tz as text), '') || '-' || coalesce(cast(time_no_tz as text), '') || '-' || coalesce(cast(property_binary_data as text), '') as text)) as _airbyte_exchange_rate_hashid,
    tmp.*
from __dbt__cte__exchange_rate_ab2 tmp
-- exchange_rate
where 1 = 1
)-- Final base SQL model
-- depends_on: __dbt__cte__exchange_rate_ab3
select
    "id",
    currency,
    "date",
    timestamp_col,
    "HKD@spéçiäl & characters",
    hkd_special___characters,
    nzd,
    usd,
    "column`_'with""_quotes",
    datetime_tz,
    datetime_no_tz,
    time_tz,
    time_no_tz,
    property_binary_data,
    _airbyte_ab_id,
    _airbyte_emitted_at,
    now() as _airbyte_normalized_at,
    _airbyte_exchange_rate_hashid
from __dbt__cte__exchange_rate_ab3
-- exchange_rate from "postgres".test_normalization._airbyte_raw_exchange_rate
where 1 = 1
  );