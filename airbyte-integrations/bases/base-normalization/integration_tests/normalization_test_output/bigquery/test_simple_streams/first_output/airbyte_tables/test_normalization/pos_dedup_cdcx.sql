

  create or replace table `dataline-integration-testing`.test_normalization.`pos_dedup_cdcx`
  partition by timestamp_trunc(_airbyte_emitted_at, day)
  cluster by _airbyte_unique_key, _airbyte_emitted_at
  OPTIONS()
  as (
    
-- Final base SQL model
select
    _airbyte_unique_key,
    id,
    name,
    _ab_cdc_lsn,
    _ab_cdc_updated_at,
    _ab_cdc_deleted_at,
    _ab_cdc_log_pos,
    _airbyte_ab_id,
    _airbyte_emitted_at,
    CURRENT_TIMESTAMP() as _airbyte_normalized_at,
    _airbyte_pos_dedup_cdcx_hashid
from `dataline-integration-testing`.test_normalization.`pos_dedup_cdcx_scd`
-- pos_dedup_cdcx from `dataline-integration-testing`.test_normalization._airbyte_raw_pos_dedup_cdcx
where 1 = 1
and _airbyte_active_row = 1
  );
    