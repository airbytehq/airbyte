

  create or replace table `dataline-integration-testing`.test_normalization.`exchange_rate`
  partition by timestamp_trunc(_airbyte_emitted_at, day)
  cluster by _airbyte_emitted_at
  OPTIONS()
  as (
    
with __dbt__cte__exchange_rate_ab1 as (

-- SQL model to parse JSON blob stored in a single column and extract into separated field columns as described by the JSON Schema
-- depends_on: `dataline-integration-testing`.test_normalization._airbyte_raw_exchange_rate
select
    json_extract_scalar(_airbyte_data, "$['id']") as id,
    json_extract_scalar(_airbyte_data, "$['currency']") as currency,
    json_extract_scalar(_airbyte_data, "$['date']") as date,
    json_extract_scalar(_airbyte_data, "$['timestamp_col']") as timestamp_col,
    json_extract_scalar(_airbyte_data, "$['HKD@spéçiäl & characters']") as HKD_special___characters,
    json_extract_scalar(_airbyte_data, "$['HKD_special___characters']") as HKD_special___characters_1,
    json_extract_scalar(_airbyte_data, "$['NZD']") as NZD,
    json_extract_scalar(_airbyte_data, "$['USD']") as USD,
    json_extract_scalar(_airbyte_data, "$['column___with__quotes']") as column___with__quotes,
    json_extract_scalar(_airbyte_data, "$['datetime_tz']") as datetime_tz,
    json_extract_scalar(_airbyte_data, "$['datetime_no_tz']") as datetime_no_tz,
    json_extract_scalar(_airbyte_data, "$['time_tz']") as time_tz,
    json_extract_scalar(_airbyte_data, "$['time_no_tz']") as time_no_tz,
    json_extract_scalar(_airbyte_data, "$['property_binary_data']") as property_binary_data,
    _airbyte_ab_id,
    _airbyte_emitted_at,
    CURRENT_TIMESTAMP() as _airbyte_normalized_at
from `dataline-integration-testing`.test_normalization._airbyte_raw_exchange_rate as table_alias
-- exchange_rate
where 1 = 1
),  __dbt__cte__exchange_rate_ab2 as (

-- SQL model to cast each column to its adequate SQL type converted from the JSON schema type
-- depends_on: __dbt__cte__exchange_rate_ab1
select
    cast(id as 
    int64
) as id,
    cast(currency as 
    string
) as currency,
    cast(nullif(date, '') as 
    date
) as date,
    cast(nullif(timestamp_col, '') as 
    timestamp
) as timestamp_col,
    cast(HKD_special___characters as 
    float64
) as HKD_special___characters,
    cast(HKD_special___characters_1 as 
    string
) as HKD_special___characters_1,
    cast(NZD as 
    float64
) as NZD,
    cast(USD as 
    float64
) as USD,
    cast(column___with__quotes as 
    string
) as column___with__quotes,
    cast(nullif(datetime_tz, '') as 
    timestamp
) as datetime_tz,
    cast(nullif(datetime_no_tz, '') as 
    datetime
) as datetime_no_tz,
    cast(nullif(time_tz, '') as 
    STRING
) as time_tz,
    cast(nullif(time_no_tz, '') as 
    time
) as time_no_tz,
    cast(FROM_BASE64(property_binary_data) as bytes) as property_binary_data,
    _airbyte_ab_id,
    _airbyte_emitted_at,
    CURRENT_TIMESTAMP() as _airbyte_normalized_at
from __dbt__cte__exchange_rate_ab1
-- exchange_rate
where 1 = 1
),  __dbt__cte__exchange_rate_ab3 as (

-- SQL model to build a hash column based on the values of this record
-- depends_on: __dbt__cte__exchange_rate_ab2
select
    to_hex(md5(cast(concat(coalesce(cast(id as 
    string
), ''), '-', coalesce(cast(currency as 
    string
), ''), '-', coalesce(cast(date as 
    string
), ''), '-', coalesce(cast(timestamp_col as 
    string
), ''), '-', coalesce(cast(HKD_special___characters as 
    string
), ''), '-', coalesce(cast(HKD_special___characters_1 as 
    string
), ''), '-', coalesce(cast(NZD as 
    string
), ''), '-', coalesce(cast(USD as 
    string
), ''), '-', coalesce(cast(column___with__quotes as 
    string
), ''), '-', coalesce(cast(datetime_tz as 
    string
), ''), '-', coalesce(cast(datetime_no_tz as 
    string
), ''), '-', coalesce(cast(time_tz as 
    string
), ''), '-', coalesce(cast(time_no_tz as 
    string
), ''), '-', coalesce(cast(property_binary_data as 
    string
), '')) as 
    string
))) as _airbyte_exchange_rate_hashid,
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
    HKD_special___characters,
    HKD_special___characters_1,
    NZD,
    USD,
    column___with__quotes,
    datetime_tz,
    datetime_no_tz,
    time_tz,
    time_no_tz,
    property_binary_data,
    _airbyte_ab_id,
    _airbyte_emitted_at,
    CURRENT_TIMESTAMP() as _airbyte_normalized_at,
    _airbyte_exchange_rate_hashid
from __dbt__cte__exchange_rate_ab3
-- exchange_rate from `dataline-integration-testing`.test_normalization._airbyte_raw_exchange_rate
where 1 = 1
  );
  