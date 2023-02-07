

      create or replace  table "INTEGRATION_TEST_NORMALIZATION".TEST_NORMALIZATION."EXCHANGE_RATE"  as
      (select * from(
            
with __dbt__cte__EXCHANGE_RATE_AB1 as (

-- SQL model to parse JSON blob stored in a single column and extract into separated field columns as described by the JSON Schema
-- depends_on: "INTEGRATION_TEST_NORMALIZATION".TEST_NORMALIZATION._AIRBYTE_RAW_EXCHANGE_RATE
select
    to_varchar(get_path(parse_json(_airbyte_data), '"id"')) as ID,
    to_varchar(get_path(parse_json(_airbyte_data), '"currency"')) as CURRENCY,
    to_varchar(get_path(parse_json(_airbyte_data), '"date"')) as DATE,
    to_varchar(get_path(parse_json(_airbyte_data), '"timestamp_col"')) as TIMESTAMP_COL,
    to_varchar(get_path(parse_json(_airbyte_data), '"HKD@spéçiäl & characters"')) as "HKD@spéçiäl & characters",
    to_varchar(get_path(parse_json(_airbyte_data), '"HKD_special___characters"')) as HKD_SPECIAL___CHARACTERS,
    to_varchar(get_path(parse_json(_airbyte_data), '"NZD"')) as NZD,
    to_varchar(get_path(parse_json(_airbyte_data), '"USD"')) as USD,
    to_varchar(get_path(parse_json(_airbyte_data), '"column`_''with""_quotes"')) as "column`_'with""_quotes",
    to_varchar(get_path(parse_json(_airbyte_data), '"datetime_tz"')) as DATETIME_TZ,
    to_varchar(get_path(parse_json(_airbyte_data), '"datetime_no_tz"')) as DATETIME_NO_TZ,
    to_varchar(get_path(parse_json(_airbyte_data), '"time_tz"')) as TIME_TZ,
    to_varchar(get_path(parse_json(_airbyte_data), '"time_no_tz"')) as TIME_NO_TZ,
    to_varchar(get_path(parse_json(_airbyte_data), '"property_binary_data"')) as PROPERTY_BINARY_DATA,
    _AIRBYTE_AB_ID,
    _AIRBYTE_EMITTED_AT,
    convert_timezone('UTC', current_timestamp()) as _AIRBYTE_NORMALIZED_AT
from "INTEGRATION_TEST_NORMALIZATION".TEST_NORMALIZATION._AIRBYTE_RAW_EXCHANGE_RATE as table_alias
-- EXCHANGE_RATE
where 1 = 1
),  __dbt__cte__EXCHANGE_RATE_AB2 as (

-- SQL model to cast each column to its adequate SQL type converted from the JSON schema type
-- depends_on: __dbt__cte__EXCHANGE_RATE_AB1
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
    cast("column`_'with""_quotes" as 
    varchar
) as "column`_'with""_quotes",
    case
        when DATETIME_TZ regexp '\\d{4}-\\d{2}-\\d{2}T(\\d{2}:){2}\\d{2}(\\+|-)\\d{4}' then to_timestamp_tz(DATETIME_TZ, 'YYYY-MM-DDTHH24:MI:SSTZHTZM')
        when DATETIME_TZ regexp '\\d{4}-\\d{2}-\\d{2}T(\\d{2}:){2}\\d{2}(\\+|-)\\d{2}' then to_timestamp_tz(DATETIME_TZ, 'YYYY-MM-DDTHH24:MI:SSTZH')
        when DATETIME_TZ regexp '\\d{4}-\\d{2}-\\d{2}T(\\d{2}:){2}\\d{2}\\.\\d{1,7}(\\+|-)\\d{4}' then to_timestamp_tz(DATETIME_TZ, 'YYYY-MM-DDTHH24:MI:SS.FFTZHTZM')
        when DATETIME_TZ regexp '\\d{4}-\\d{2}-\\d{2}T(\\d{2}:){2}\\d{2}\\.\\d{1,7}(\\+|-)\\d{2}' then to_timestamp_tz(DATETIME_TZ, 'YYYY-MM-DDTHH24:MI:SS.FFTZH')
        when DATETIME_TZ = '' then NULL
    else to_timestamp_tz(DATETIME_TZ)
    end as DATETIME_TZ
    ,
    case
        when DATETIME_NO_TZ regexp '\\d{4}-\\d{2}-\\d{2}T(\\d{2}:){2}\\d{2}' then to_timestamp(DATETIME_NO_TZ, 'YYYY-MM-DDTHH24:MI:SS')
        when DATETIME_NO_TZ regexp '\\d{4}-\\d{2}-\\d{2}T(\\d{2}:){2}\\d{2}\\.\\d{1,7}' then to_timestamp(DATETIME_NO_TZ, 'YYYY-MM-DDTHH24:MI:SS.FF')
        when DATETIME_NO_TZ = '' then NULL
    else to_timestamp(DATETIME_NO_TZ)
    end as DATETIME_NO_TZ
    ,
    cast(nullif(TIME_TZ, '') as 
    varchar
) as TIME_TZ,
    cast(nullif(TIME_NO_TZ, '') as 
    time
) as TIME_NO_TZ,
    cast(BASE64_DECODE_BINARY(PROPERTY_BINARY_DATA) as VARBINARY) as PROPERTY_BINARY_DATA,
    _AIRBYTE_AB_ID,
    _AIRBYTE_EMITTED_AT,
    convert_timezone('UTC', current_timestamp()) as _AIRBYTE_NORMALIZED_AT
from __dbt__cte__EXCHANGE_RATE_AB1
-- EXCHANGE_RATE
where 1 = 1
),  __dbt__cte__EXCHANGE_RATE_AB3 as (

-- SQL model to build a hash column based on the values of this record
-- depends_on: __dbt__cte__EXCHANGE_RATE_AB2
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
), '') || '-' || coalesce(cast("column`_'with""_quotes" as 
    varchar
), '') || '-' || coalesce(cast(DATETIME_TZ as 
    varchar
), '') || '-' || coalesce(cast(DATETIME_NO_TZ as 
    varchar
), '') || '-' || coalesce(cast(TIME_TZ as 
    varchar
), '') || '-' || coalesce(cast(TIME_NO_TZ as 
    varchar
), '') || '-' || coalesce(cast(PROPERTY_BINARY_DATA as 
    varchar
), '') as 
    varchar
)) as _AIRBYTE_EXCHANGE_RATE_HASHID,
    tmp.*
from __dbt__cte__EXCHANGE_RATE_AB2 tmp
-- EXCHANGE_RATE
where 1 = 1
)-- Final base SQL model
-- depends_on: __dbt__cte__EXCHANGE_RATE_AB3
select
    ID,
    CURRENCY,
    DATE,
    TIMESTAMP_COL,
    "HKD@spéçiäl & characters",
    HKD_SPECIAL___CHARACTERS,
    NZD,
    USD,
    "column`_'with""_quotes",
    DATETIME_TZ,
    DATETIME_NO_TZ,
    TIME_TZ,
    TIME_NO_TZ,
    PROPERTY_BINARY_DATA,
    _AIRBYTE_AB_ID,
    _AIRBYTE_EMITTED_AT,
    convert_timezone('UTC', current_timestamp()) as _AIRBYTE_NORMALIZED_AT,
    _AIRBYTE_EXCHANGE_RATE_HASHID
from __dbt__cte__EXCHANGE_RATE_AB3
-- EXCHANGE_RATE from "INTEGRATION_TEST_NORMALIZATION".TEST_NORMALIZATION._AIRBYTE_RAW_EXCHANGE_RATE
where 1 = 1
            ) order by (_AIRBYTE_EMITTED_AT)
      );
    alter table "INTEGRATION_TEST_NORMALIZATION".TEST_NORMALIZATION."EXCHANGE_RATE" cluster by (_AIRBYTE_EMITTED_AT);