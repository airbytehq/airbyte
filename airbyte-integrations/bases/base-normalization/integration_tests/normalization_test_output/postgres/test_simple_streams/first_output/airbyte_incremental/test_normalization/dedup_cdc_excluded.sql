
      

  create  table "postgres".test_normalization."dedup_cdc_excluded"
  as (
    
-- Final base SQL model
-- depends_on: "postgres".test_normalization."dedup_cdc_excluded_scd"
select
    _airbyte_unique_key,
    "id",
    "name",
    _ab_cdc_lsn,
    _ab_cdc_updated_at,
    _ab_cdc_deleted_at,
    _airbyte_ab_id,
    _airbyte_emitted_at,
    now() as _airbyte_normalized_at,
    _airbyte_dedup_cdc_excluded_hashid
from "postgres".test_normalization."dedup_cdc_excluded_scd"
-- dedup_cdc_excluded from "postgres".test_normalization._airbyte_raw_dedup_cdc_excluded
where 1 = 1
and _airbyte_active_row = 1

  );
  