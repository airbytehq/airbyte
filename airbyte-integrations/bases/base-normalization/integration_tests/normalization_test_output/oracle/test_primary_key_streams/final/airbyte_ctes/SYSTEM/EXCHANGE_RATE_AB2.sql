
  create view SYSTEM.EXCHANGE_RATE_AB2__dbt_tmp as
    
-- SQL model to cast each column to its adequate SQL type converted from the JSON schema type
select
    cast(ID as 
    numeric
) as ID,
    cast(CURRENCY as varchar(1000)) as CURRENCY,
    cast("DATE" as varchar(1000)) as "DATE",
    cast(TIMESTAMP_COL as varchar(1000)) as TIMESTAMP_COL,
    cast(HKD_SPECIAL___CHARACTERS as 
    numeric
) as HKD_SPECIAL___CHARACTERS,
    cast(HKD_SPECIAL___CHARACTERS_1 as varchar(1000)) as HKD_SPECIAL___CHARACTERS_1,
    cast(NZD as 
    numeric
) as NZD,
    cast(USD as 
    numeric
) as USD,
    airbyte_emitted_at
from SYSTEM.EXCHANGE_RATE_AB1
-- EXCHANGE_RATE

