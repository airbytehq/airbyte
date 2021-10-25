

  create or replace view `dataline-integration-testing`._airbyte_test_normalization.`pos_dedup_cdcx_ab2`
  OPTIONS()
  as 
-- SQL model to cast each column to its adequate SQL type converted from the JSON schema type
select
    cast(id as 
    int64
) as id,
    cast(name as 
    string
) as name,
    cast(_ab_cdc_lsn as 
    float64
) as _ab_cdc_lsn,
    cast(_ab_cdc_updated_at as 
    float64
) as _ab_cdc_updated_at,
    cast(_ab_cdc_deleted_at as 
    float64
) as _ab_cdc_deleted_at,
    cast(_ab_cdc_log_pos as 
    float64
) as _ab_cdc_log_pos,
    _airbyte_emitted_at
from `dataline-integration-testing`._airbyte_test_normalization.`pos_dedup_cdcx_ab1`
-- pos_dedup_cdcx;

