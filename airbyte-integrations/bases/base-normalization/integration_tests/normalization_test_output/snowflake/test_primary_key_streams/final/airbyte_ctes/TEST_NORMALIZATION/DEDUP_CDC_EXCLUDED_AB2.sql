
  create or replace  view "AIRBYTE_DATABASE"._AIRBYTE_TEST_NORMALIZATION."DEDUP_CDC_EXCLUDED_AB2"  as (
    
-- SQL model to cast each column to its adequate SQL type converted from the JSON schema type
select
    cast(ID as 
    bigint
) as ID,
    cast(NAME as 
    varchar
) as NAME,
    cast(_AB_CDC_LSN as 
    float
) as _AB_CDC_LSN,
    cast(_AB_CDC_UPDATED_AT as 
    float
) as _AB_CDC_UPDATED_AT,
    cast(_AB_CDC_DELETED_AT as 
    float
) as _AB_CDC_DELETED_AT,
    _airbyte_emitted_at
from "AIRBYTE_DATABASE"._AIRBYTE_TEST_NORMALIZATION."DEDUP_CDC_EXCLUDED_AB1"
-- DEDUP_CDC_EXCLUDED
  );
