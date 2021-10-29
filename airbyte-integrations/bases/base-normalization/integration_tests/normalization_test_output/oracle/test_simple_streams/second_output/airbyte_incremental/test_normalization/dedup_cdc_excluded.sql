

  create  table test_normalization.dedup_cdc_excluded__dbt_tmp
  
  as
    
-- Final base SQL model
select
    "_AIRBYTE_UNIQUE_KEY",
    id,
    name,
    "_AB_CDC_LSN",
    "_AB_CDC_UPDATED_AT",
    "_AB_CDC_DELETED_AT",
    "_AIRBYTE_AB_ID",
    "_AIRBYTE_EMITTED_AT",
    
    CURRENT_TIMESTAMP
 as "_AIRBYTE_NORMALIZED_AT",
    "_AIRBYTE_DEDUP_CDC_EXCLUDED_HASHID"
from test_normalization.dedup_cdc_excluded_scd
-- dedup_cdc_excluded from test_normalization.airbyte_raw_dedup_cdc_excluded
where 1 = 1
and "_AIRBYTE_ACTIVE_ROW" = 1
