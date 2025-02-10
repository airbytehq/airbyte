
  create or replace  view "INTEGRATION_TEST_NORMALIZATION"._AIRBYTE_TEST_NORMALIZATION."DEDUP_EXCHANGE_RATE_STG" 
  
   as (
    
with __dbt__cte__DEDUP_EXCHANGE_RATE_AB1 as (

-- SQL model to parse JSON blob stored in a single column and extract into separated field columns as described by the JSON Schema
-- depends_on: "INTEGRATION_TEST_NORMALIZATION".TEST_NORMALIZATION._AIRBYTE_RAW_DEDUP_EXCHANGE_RATE
select
    to_varchar(get_path(parse_json(_airbyte_data), '"id"')) as ID,
    to_varchar(get_path(parse_json(_airbyte_data), '"currency"')) as CURRENCY,
    to_varchar(get_path(parse_json(_airbyte_data), '"date"')) as DATE,
    to_varchar(get_path(parse_json(_airbyte_data), '"timestamp_col"')) as TIMESTAMP_COL,
    to_varchar(get_path(parse_json(_airbyte_data), '"HKD@spéçiäl & characters"')) as "HKD@spéçiäl & characters",
    to_varchar(get_path(parse_json(_airbyte_data), '"HKD_special___characters"')) as HKD_SPECIAL___CHARACTERS,
    to_varchar(get_path(parse_json(_airbyte_data), '"NZD"')) as NZD,
    to_varchar(get_path(parse_json(_airbyte_data), '"USD"')) as USD,
    _AIRBYTE_AB_ID,
    _AIRBYTE_EMITTED_AT,
    convert_timezone('UTC', current_timestamp()) as _AIRBYTE_NORMALIZED_AT
from "INTEGRATION_TEST_NORMALIZATION".TEST_NORMALIZATION._AIRBYTE_RAW_DEDUP_EXCHANGE_RATE as table_alias
-- DEDUP_EXCHANGE_RATE
where 1 = 1

),  __dbt__cte__DEDUP_EXCHANGE_RATE_AB2 as (

-- SQL model to cast each column to its adequate SQL type converted from the JSON schema type
-- depends_on: __dbt__cte__DEDUP_EXCHANGE_RATE_AB1
select
    cast(ID as 
    bigint
) as ID,
    cast(CURRENCY as 
    varchar
) as CURRENCY,
    cast(nullif(DATE, '') as 
    date
) as DATE,
    case
        when TIMESTAMP_COL regexp '\\d{4}-\\d{2}-\\d{2}T(\\d{2}:){2}\\d{2}(\\+|-)\\d{4}' then to_timestamp_tz(TIMESTAMP_COL, 'YYYY-MM-DDTHH24:MI:SSTZHTZM')
        when TIMESTAMP_COL regexp '\\d{4}-\\d{2}-\\d{2}T(\\d{2}:){2}\\d{2}(\\+|-)\\d{2}' then to_timestamp_tz(TIMESTAMP_COL, 'YYYY-MM-DDTHH24:MI:SSTZH')
        when TIMESTAMP_COL regexp '\\d{4}-\\d{2}-\\d{2}T(\\d{2}:){2}\\d{2}\\.\\d{1,7}(\\+|-)\\d{4}' then to_timestamp_tz(TIMESTAMP_COL, 'YYYY-MM-DDTHH24:MI:SS.FFTZHTZM')
        when TIMESTAMP_COL regexp '\\d{4}-\\d{2}-\\d{2}T(\\d{2}:){2}\\d{2}\\.\\d{1,7}(\\+|-)\\d{2}' then to_timestamp_tz(TIMESTAMP_COL, 'YYYY-MM-DDTHH24:MI:SS.FFTZH')
        when TIMESTAMP_COL = '' then NULL
    else to_timestamp_tz(TIMESTAMP_COL)
    end as TIMESTAMP_COL
    ,
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
    _AIRBYTE_AB_ID,
    _AIRBYTE_EMITTED_AT,
    convert_timezone('UTC', current_timestamp()) as _AIRBYTE_NORMALIZED_AT
from __dbt__cte__DEDUP_EXCHANGE_RATE_AB1
-- DEDUP_EXCHANGE_RATE
where 1 = 1

)-- SQL model to build a hash column based on the values of this record
-- depends_on: __dbt__cte__DEDUP_EXCHANGE_RATE_AB2
select
    md5(cast(coalesce(cast(ID as 
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
), '') as 
    varchar
)) as _AIRBYTE_DEDUP_EXCHANGE_RATE_HASHID,
    tmp.*
from __dbt__cte__DEDUP_EXCHANGE_RATE_AB2 tmp
-- DEDUP_EXCHANGE_RATE
where 1 = 1

  );
