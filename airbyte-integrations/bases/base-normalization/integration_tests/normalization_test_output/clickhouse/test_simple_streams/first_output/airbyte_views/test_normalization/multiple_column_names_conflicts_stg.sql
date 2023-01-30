

  create view _airbyte_test_normalization.multiple_column_names_conflicts_stg 
  
  as (
    
-- SQL model to build a hash column based on the values of this record
-- depends_on: _airbyte_test_normalization.multiple_column_names_conflicts_ab2
select
    assumeNotNull(hex(MD5(
            
                toString(id) || '~' ||
            
            
                toString("User Id") || '~' ||
            
            
                toString(user_id) || '~' ||
            
            
                toString("User id") || '~' ||
            
            
                toString("user id") || '~' ||
            
            
                toString("User@Id") || '~' ||
            
            
                toString(UserId)
            
    ))) as _airbyte_multiple_co__ames_conflicts_hashid,
    tmp.*
from _airbyte_test_normalization.multiple_column_names_conflicts_ab2 tmp
-- multiple_column_names_conflicts
where 1 = 1

  )