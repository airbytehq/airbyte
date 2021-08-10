
  create or replace  view "AIRBYTE_DATABASE"._AIRBYTE_TEST_NORMALIZATION."DEDUP_EXCHANGE_RATE_AB2"  as (
    
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
    _airbyte_emitted_at
from "AIRBYTE_DATABASE"._AIRBYTE_TEST_NORMALIZATION."DEDUP_EXCHANGE_RATE_AB1"
-- DEDUP_EXCHANGE_RATE
  );
