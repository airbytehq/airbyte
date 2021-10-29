

  create  table test_normalization.renamed_dedup_cdc_excluded__dbt_tmp
  
  as
    
-- Final base SQL model
select
    "_AIRBYTE_UNIQUE_KEY",
    id,
    "_AIRBYTE_AB_ID",
    "_AIRBYTE_EMITTED_AT",
    
    CURRENT_TIMESTAMP
 as "_AIRBYTE_NORMALIZED_AT",
    "_AIRBYTE_RENAMED_DEDUP_CDC_EXCLUDED_HASHID"
from test_normalization.renamed_dedup_cdc_excluded_scd
-- renamed_dedup_cdc_excluded from test_normalization.airbyte_raw_renamed_dedup_cdc_excluded
where 1 = 1
and "_AIRBYTE_ACTIVE_ROW" = 1
