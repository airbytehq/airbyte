
  create or replace  view "AIRBYTE_DATABASE"._AIRBYTE_TEST_NORMALIZATION."POS_DEDUP_CDCX_AB2"  as (
    
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
    cast(_AB_CDC_LOG_POS as 
    float
) as _AB_CDC_LOG_POS,
    _AIRBYTE_EMITTED_AT
from "AIRBYTE_DATABASE"._AIRBYTE_TEST_NORMALIZATION."POS_DEDUP_CDCX_AB1"
-- POS_DEDUP_CDCX
  );
