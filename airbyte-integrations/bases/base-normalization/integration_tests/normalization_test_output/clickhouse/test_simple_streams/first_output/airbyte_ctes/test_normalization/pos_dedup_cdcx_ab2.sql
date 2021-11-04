

  create view _airbyte_test_normalization.pos_dedup_cdcx_ab2__dbt_tmp 
  
  as (
    
-- SQL model to cast each column to its adequate SQL type converted from the JSON schema type
select
    accurateCastOrNull(id, '
    BIGINT
') as id,
    nullif(accurateCastOrNull(trim(BOTH '"' from name), 'String'), 'null') as name,
    accurateCastOrNull(_ab_cdc_lsn, '
    Float64
') as _ab_cdc_lsn,
    accurateCastOrNull(_ab_cdc_updated_at, '
    Float64
') as _ab_cdc_updated_at,
    accurateCastOrNull(_ab_cdc_deleted_at, '
    Float64
') as _ab_cdc_deleted_at,
    accurateCastOrNull(_ab_cdc_log_pos, '
    Float64
') as _ab_cdc_log_pos,
    _airbyte_ab_id,
    _airbyte_emitted_at,
    now() as _airbyte_normalized_at
from _airbyte_test_normalization.pos_dedup_cdcx_ab1
-- pos_dedup_cdcx
where 1 = 1
  )