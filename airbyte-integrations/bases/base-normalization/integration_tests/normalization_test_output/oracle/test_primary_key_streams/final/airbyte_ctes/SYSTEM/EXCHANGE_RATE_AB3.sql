
  create view SYSTEM.EXCHANGE_RATE_AB3__dbt_tmp as
    
-- SQL model to build a hash column based on the values of this record
select
    ora_hash(
        'ID' || '~' ||
        'CURRENCY' || '~' ||
        "DATE" || '~' ||
        'TIMESTAMP_COL' || '~' ||
        'HKD_SPECIAL___CHARACTERS' || '~' ||
        'HKD_SPECIAL___CHARACTERS_1' || '~' ||
        'NZD' || '~' ||
        'USD'
    ) as AIRBYTE_EXCHANGE_RATE_HASHID,
    tmp.*
from SYSTEM.EXCHANGE_RATE_AB2 tmp
-- EXCHANGE_RATE

