
  create view SYSTEM.DEDUP_CDC_EXCLUDED_AB2__dbt_tmp as
    
-- SQL model to cast each column to its adequate SQL type converted from the JSON schema type
select
    cast(ID as 
    numeric
) as ID,
    cast(NAME as varchar(1000)) as NAME,
    cast("_AB_CDC_LSN" as 
    numeric
) as "_AB_CDC_LSN",
    cast("_AB_CDC_UPDATED_AT" as 
    numeric
) as "_AB_CDC_UPDATED_AT",
    cast("_AB_CDC_DELETED_AT" as 
    numeric
) as "_AB_CDC_DELETED_AT",
    airbyte_emitted_at
from SYSTEM.DEDUP_CDC_EXCLUDED_AB1
-- DEDUP_CDC_EXCLUDED

