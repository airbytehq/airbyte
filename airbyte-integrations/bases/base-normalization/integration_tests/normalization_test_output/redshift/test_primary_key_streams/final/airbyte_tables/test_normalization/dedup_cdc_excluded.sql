

  create  table
    "integrationtests".test_normalization."dedup_cdc_excluded__dbt_tmp"
    
    
  as (
    
-- Final base SQL model
select
    id,
    name,
    _ab_cdc_lsn,
    _ab_cdc_updated_at,
    _ab_cdc_deleted_at,
    _airbyte_emitted_at,
    _airbyte_dedup_cdc_excluded_hashid
from "integrationtests".test_normalization."dedup_cdc_excluded_scd"
-- dedup_cdc_excluded from "integrationtests".test_normalization._airbyte_raw_dedup_cdc_excluded
where _airbyte_active_row = 1
  );