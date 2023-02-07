

  create  table
    "normalization_tests".test_normalization_vorny."exchange_rate__dbt_tmp"
    
    
      compound sortkey(_airbyte_emitted_at)
    
  as (
    
with __dbt__cte__exchange_rate_ab1 as (

-- SQL model to parse JSON blob stored in a single column and extract into separated field columns as described by the JSON Schema
-- depends_on: "normalization_tests".test_normalization_vorny._airbyte_raw_exchange_rate
select
    case when _airbyte_data."id" != '' then _airbyte_data."id" end as id,
    case when _airbyte_data."currency" != '' then _airbyte_data."currency" end as currency,
    case when _airbyte_data."new_column" != '' then _airbyte_data."new_column" end as new_column,
    case when _airbyte_data."date" != '' then _airbyte_data."date" end as date,
    case when _airbyte_data."timestamp_col" != '' then _airbyte_data."timestamp_col" end as timestamp_col,
    case when _airbyte_data."HKD@spéçiäl & characters" != '' then _airbyte_data."HKD@spéçiäl & characters" end as "hkd@spéçiäl & characters",
    case when _airbyte_data."NZD" != '' then _airbyte_data."NZD" end as nzd,
    case when _airbyte_data."USD" != '' then _airbyte_data."USD" end as usd,
    case when _airbyte_data."column`_'with""_quotes" != '' then _airbyte_data."column`_'with""_quotes" end as "column`_'with""_quotes",
    _airbyte_ab_id,
    _airbyte_emitted_at,
    getdate() as _airbyte_normalized_at
from "normalization_tests".test_normalization_vorny._airbyte_raw_exchange_rate as table_alias
-- exchange_rate
where 1 = 1
),  __dbt__cte__exchange_rate_ab2 as (

-- SQL model to cast each column to its adequate SQL type converted from the JSON schema type
-- depends_on: __dbt__cte__exchange_rate_ab1
select
    cast(id as 
    float
) as id,
    cast(currency as text) as currency,
    cast(new_column as 
    float
) as new_column,
    cast(nullif(date::varchar, '') as 
    date
) as date,
    cast(nullif(timestamp_col::varchar, '') as 
    TIMESTAMPTZ
) as timestamp_col,
    cast("hkd@spéçiäl & characters" as 
    float
) as "hkd@spéçiäl & characters",
    cast(nzd as 
    float
) as nzd,
    cast(usd as 
    float
) as usd,
    cast("column`_'with""_quotes" as text) as "column`_'with""_quotes",
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
    md5(cast(coalesce(cast(id as text), '') || '-' || coalesce(cast(currency as text), '') || '-' || coalesce(cast(new_column as text), '') || '-' || coalesce(cast(date as text), '') || '-' || coalesce(cast(timestamp_col as text), '') || '-' || coalesce(cast("hkd@spéçiäl & characters" as text), '') || '-' || coalesce(cast(nzd as text), '') || '-' || coalesce(cast(usd as text), '') || '-' || coalesce(cast("column`_'with""_quotes" as text), '') as text)) as _airbyte_exchange_rate_hashid,
    tmp.*
from __dbt__cte__exchange_rate_ab2 tmp
-- exchange_rate
where 1 = 1
)-- Final base SQL model
-- depends_on: __dbt__cte__exchange_rate_ab3
select
    id,
    currency,
    new_column,
    date,
    timestamp_col,
    "hkd@spéçiäl & characters",
    nzd,
    usd,
    "column`_'with""_quotes",
    _airbyte_ab_id,
    _airbyte_emitted_at,
    getdate() as _airbyte_normalized_at,
    _airbyte_exchange_rate_hashid
from __dbt__cte__exchange_rate_ab3
-- exchange_rate from "normalization_tests".test_normalization_vorny._airbyte_raw_exchange_rate
where 1 = 1
  );