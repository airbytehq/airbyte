

  create or replace view `dataline-integration-testing`._airbyte_test_normalization.`dedup_cdc_excluded_ab2`
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
    _airbyte_ab_id,
    _airbyte_emitted_at,
    CURRENT_TIMESTAMP() as _airbyte_normalized_at
from `dataline-integration-testing`._airbyte_test_normalization.`dedup_cdc_excluded_ab1`
-- dedup_cdc_excluded
where 1 = 1
;

