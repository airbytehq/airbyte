

  create view _airbyte_test_normalization.dedup_cdc_excluded_ab3__dbt_tmp 
  
  as (
    
-- SQL model to build a hash column based on the values of this record
select
    assumeNotNull(hex(MD5(
            
                toString(id) || '~' ||
            
            
                toString(name) || '~' ||
            
            
                toString(_ab_cdc_lsn) || '~' ||
            
            
                toString(_ab_cdc_updated_at) || '~' ||
            
            
                toString(_ab_cdc_deleted_at)
            
    ))) as _airbyte_dedup_cdc_excluded_hashid,
    tmp.*
from _airbyte_test_normalization.dedup_cdc_excluded_ab2 tmp
-- dedup_cdc_excluded
where 1 = 1

  )