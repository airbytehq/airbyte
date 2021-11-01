

  create  table test_normalization.pos_dedup_cdcx__dbt_tmp
  
  as
    
-- Final base SQL model
select
    "_AIRBYTE_UNIQUE_KEY",
    id,
    name,
    "_AB_CDC_LSN",
    "_AB_CDC_UPDATED_AT",
    "_AB_CDC_DELETED_AT",
    "_AB_CDC_LOG_POS",
    "_AIRBYTE_AB_ID",
    "_AIRBYTE_EMITTED_AT",
    
    CURRENT_TIMESTAMP
 as "_AIRBYTE_NORMALIZED_AT",
    "_AIRBYTE_POS_DEDUP_CDCX_HASHID"
from test_normalization.pos_dedup_cdcx_scd
-- pos_dedup_cdcx from test_normalization.airbyte_raw_pos_dedup_cdcx
where 1 = 1
and "_AIRBYTE_ACTIVE_ROW" = 1