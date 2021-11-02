
      

  create  table
    "integrationtests"."test_normalization"."renamed_dedup_cdc_excluded__dbt_tmp"
    
    
      compound sortkey(_airbyte_unique_key,_airbyte_emitted_at)
  as (
    
-- Final base SQL model
select
    _airbyte_unique_key,
    id,
    _airbyte_ab_id,
    _airbyte_emitted_at,
    getdate() as _airbyte_normalized_at,
    _airbyte_renamed_dedup_cdc_excluded_hashid
from "integrationtests".test_normalization."renamed_dedup_cdc_excluded_scd"
-- renamed_dedup_cdc_excluded from "integrationtests".test_normalization._airbyte_raw_renamed_dedup_cdc_excluded
where 1 = 1
and _airbyte_active_row = 1

  );
  