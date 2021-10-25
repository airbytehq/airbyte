
  create or replace  view "AIRBYTE_DATABASE"._AIRBYTE_TEST_NORMALIZATION."EXCHANGE_RATE_AB2"  as (
    
-- SQL model to cast each column to its adequate SQL type converted from the JSON schema type
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
    _AIRBYTE_EMITTED_AT
from "AIRBYTE_DATABASE"._AIRBYTE_TEST_NORMALIZATION."EXCHANGE_RATE_AB1"
-- EXCHANGE_RATE
  );
