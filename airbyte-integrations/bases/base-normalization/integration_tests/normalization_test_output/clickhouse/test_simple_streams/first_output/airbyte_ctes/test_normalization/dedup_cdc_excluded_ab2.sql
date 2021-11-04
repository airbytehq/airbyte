

  create view _airbyte_test_normalization.dedup_cdc_excluded_ab2__dbt_tmp 
  
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
    _airbyte_ab_id,
    _airbyte_emitted_at,
    now() as _airbyte_normalized_at
from _airbyte_test_normalization.dedup_cdc_excluded_ab1
-- dedup_cdc_excluded
where 1 = 1

  )