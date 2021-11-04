

  create view _airbyte_test_normalization.pos_dedup_cdcx_ab3__dbt_tmp 
  
  as (
    
-- SQL model to build a hash column based on the values of this record
select
    assumeNotNull(hex(MD5(
            
                toString(id) || '~' ||
            
            
                toString(name) || '~' ||
            
            
                toString(_ab_cdc_lsn) || '~' ||
            
            
                toString(_ab_cdc_updated_at) || '~' ||
            
            
                toString(_ab_cdc_deleted_at) || '~' ||
            
            
                toString(_ab_cdc_log_pos)
            
    ))) as _airbyte_pos_dedup_cdcx_hashid,
    tmp.*
from _airbyte_test_normalization.pos_dedup_cdcx_ab2 tmp
-- pos_dedup_cdcx
where 1 = 1
  )