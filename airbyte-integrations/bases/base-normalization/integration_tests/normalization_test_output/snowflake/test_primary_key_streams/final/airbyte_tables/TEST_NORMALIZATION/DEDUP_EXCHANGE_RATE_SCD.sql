

      create or replace transient table "AIRBYTE_DATABASE".TEST_NORMALIZATION."DEDUP_EXCHANGE_RATE_SCD"  as
      (
with __dbt__CTE__DEDUP_EXCHANGE_RATE_AB1 as (

-- SQL model to parse JSON blob stored in a single column and extract into separated field columns as described by the JSON Schema
select
    to_varchar(get_path(parse_json(_airbyte_data), '"id"')) as ID,
    to_varchar(get_path(parse_json(_airbyte_data), '"currency"')) as CURRENCY,
    to_varchar(get_path(parse_json(_airbyte_data), '"date"')) as DATE,
    to_varchar(get_path(parse_json(_airbyte_data), '"timestamp_col"')) as TIMESTAMP_COL,
    to_varchar(get_path(parse_json(_airbyte_data), '"HKD@spéçiäl & characters"')) as "HKD@spéçiäl & characters",
    to_varchar(get_path(parse_json(_airbyte_data), '"HKD_special___characters"')) as HKD_SPECIAL___CHARACTERS,
    to_varchar(get_path(parse_json(_airbyte_data), '"NZD"')) as NZD,
    to_varchar(get_path(parse_json(_airbyte_data), '"USD"')) as USD,
    _AIRBYTE_EMITTED_AT
from "AIRBYTE_DATABASE".TEST_NORMALIZATION._AIRBYTE_RAW_DEDUP_EXCHANGE_RATE as table_alias
-- DEDUP_EXCHANGE_RATE
),  __dbt__CTE__DEDUP_EXCHANGE_RATE_AB2 as (

-- SQL model to cast each column to its adequate SQL type converted from the JSON schema type
select
    cast(ID as 
    bigint
) as ID,
    cast(CURRENCY as 
    varchar
) as CURRENCY,
    cast(DATE as 
    date
) as DATE,
    cast(TIMESTAMP_COL as 
    timestamp with time zone
) as TIMESTAMP_COL,
    cast("HKD@spéçiäl & characters" as 
    float
) as "HKD@spéçiäl & characters",
    cast(HKD_SPECIAL___CHARACTERS as 
    varchar
) as HKD_SPECIAL___CHARACTERS,
    cast(NZD as 
    float
) as NZD,
    cast(USD as 
    float
) as USD,
    _AIRBYTE_EMITTED_AT
from __dbt__CTE__DEDUP_EXCHANGE_RATE_AB1
-- DEDUP_EXCHANGE_RATE
),  __dbt__CTE__DEDUP_EXCHANGE_RATE_AB3 as (

-- SQL model to build a hash column based on the values of this record
select
    md5(cast(
    
    coalesce(cast(ID as 
    varchar
), '') || '-' || coalesce(cast(CURRENCY as 
    varchar
), '') || '-' || coalesce(cast(DATE as 
    varchar
), '') || '-' || coalesce(cast(TIMESTAMP_COL as 
    varchar
), '') || '-' || coalesce(cast("HKD@spéçiäl & characters" as 
    varchar
), '') || '-' || coalesce(cast(HKD_SPECIAL___CHARACTERS as 
    varchar
), '') || '-' || coalesce(cast(NZD as 
    varchar
), '') || '-' || coalesce(cast(USD as 
    varchar
), '')

 as 
    varchar
)) as _AIRBYTE_DEDUP_EXCHANGE_RATE_HASHID,
    tmp.*
from __dbt__CTE__DEDUP_EXCHANGE_RATE_AB2 tmp
-- DEDUP_EXCHANGE_RATE
),  __dbt__CTE__DEDUP_EXCHANGE_RATE_AB4 as (

-- SQL model to prepare for deduplicating records based on the hash record column
select
  row_number() over (
    partition by _AIRBYTE_DEDUP_EXCHANGE_RATE_HASHID
    order by _AIRBYTE_EMITTED_AT asc
  ) as _AIRBYTE_ROW_NUM,
  tmp.*
from __dbt__CTE__DEDUP_EXCHANGE_RATE_AB3 tmp
-- DEDUP_EXCHANGE_RATE from "AIRBYTE_DATABASE".TEST_NORMALIZATION._AIRBYTE_RAW_DEDUP_EXCHANGE_RATE
)-- SQL model to build a Type 2 Slowly Changing Dimension (SCD) table for each record identified by their primary key
select
    ID,
    CURRENCY,
    DATE,
    TIMESTAMP_COL,
    "HKD@spéçiäl & characters",
    HKD_SPECIAL___CHARACTERS,
    NZD,
    USD,
  DATE as _AIRBYTE_START_AT,
  lag(DATE) over (
    partition by ID, CURRENCY, cast(NZD as 
    varchar
)
    order by DATE is null asc, DATE desc, _AIRBYTE_EMITTED_AT desc
  ) as _AIRBYTE_END_AT,
  case when lag(DATE) over (
    partition by ID, CURRENCY, cast(NZD as 
    varchar
)
    order by DATE is null asc, DATE desc, _AIRBYTE_EMITTED_AT desc
  ) is null  then 1 else 0 end as _AIRBYTE_ACTIVE_ROW,
  _AIRBYTE_EMITTED_AT,
  _AIRBYTE_DEDUP_EXCHANGE_RATE_HASHID
from __dbt__CTE__DEDUP_EXCHANGE_RATE_AB4
-- DEDUP_EXCHANGE_RATE from "AIRBYTE_DATABASE".TEST_NORMALIZATION._AIRBYTE_RAW_DEDUP_EXCHANGE_RATE
where _airbyte_row_num = 1
      );
    