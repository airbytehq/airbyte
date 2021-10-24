
  create view _airbyte_test_normalization.`pos_dedup_cdcx_ab2__dbt_tmp` as (
    
-- SQL model to cast each column to its adequate SQL type converted from the JSON schema type
select
    cast(id as 
    signed
) as id,
    cast(`name` as char) as `name`,
    cast(_ab_cdc_lsn as 
    float
) as _ab_cdc_lsn,
    cast(_ab_cdc_updated_at as 
    float
) as _ab_cdc_updated_at,
    cast(_ab_cdc_deleted_at as 
    float
) as _ab_cdc_deleted_at,
    cast(_ab_cdc_log_pos as 
    float
) as _ab_cdc_log_pos,
    _airbyte_emitted_at
from _airbyte_test_normalization.`pos_dedup_cdcx_ab1`
-- pos_dedup_cdcx
  );
