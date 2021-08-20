
  create view SYSTEM.DEDUP_CDC_EXCLUDED_AB3__dbt_tmp as
    
-- SQL model to build a hash column based on the values of this record
select
    ora_hash(
        'ID' || '~' ||
        'NAME' || '~' ||
        "_AB_CDC_LSN" || '~' ||
        "_AB_CDC_UPDATED_AT" || '~' ||
        "_AB_CDC_DELETED_AT"
    ) as AIRBYTE_DEDUP_CDC_EXCLUDED_HASHID,
    tmp.*
from SYSTEM.DEDUP_CDC_EXCLUDED_AB2 tmp
-- DEDUP_CDC_EXCLUDED

