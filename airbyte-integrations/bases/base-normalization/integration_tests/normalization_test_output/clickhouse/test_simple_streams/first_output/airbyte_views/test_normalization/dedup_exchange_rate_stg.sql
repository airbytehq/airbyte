

  create view _airbyte_test_normalization.dedup_exchange_rate_stg 
  
  as (
    
-- SQL model to build a hash column based on the values of this record
-- depends_on: _airbyte_test_normalization.dedup_exchange_rate_ab2
select
    assumeNotNull(hex(MD5(
            
                toString(id) || '~' ||
            
            
                toString(currency) || '~' ||
            
            
                toString(date) || '~' ||
            
            
                toString(timestamp_col) || '~' ||
            
            
                toString("HKD@spéçiäl & characters") || '~' ||
            
            
                toString(HKD_special___characters) || '~' ||
            
            
                toString(NZD) || '~' ||
            
            
                toString(USD)
            
    ))) as _airbyte_dedup_exchange_rate_hashid,
    tmp.*
from _airbyte_test_normalization.dedup_exchange_rate_ab2 tmp
-- dedup_exchange_rate
where 1 = 1

  )