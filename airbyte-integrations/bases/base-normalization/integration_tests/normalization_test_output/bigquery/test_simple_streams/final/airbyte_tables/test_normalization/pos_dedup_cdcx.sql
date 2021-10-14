

  create or replace table `dataline-integration-testing`.test_normalization.`pos_dedup_cdcx`
  
  
  OPTIONS()
  as (
    
-- Final base SQL model
select
    id,
    name,
    _ab_cdc_lsn,
    _ab_cdc_updated_at,
    _ab_cdc_deleted_at,
    _ab_cdc_log_pos,
    _airbyte_emitted_at,
    _airbyte_pos_dedup_cdcx_hashid
from `dataline-integration-testing`.test_normalization.`pos_dedup_cdcx_scd`
-- pos_dedup_cdcx from `dataline-integration-testing`.test_normalization._airbyte_raw_pos_dedup_cdcx
where _airbyte_active_row = 1
  );
    