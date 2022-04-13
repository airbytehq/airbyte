

  create view _airbyte_test_normalization.multiple_column_names_conflicts_stg__dbt_tmp 
  
  as (
    
with __dbt__cte__multiple_column_names_conflicts_ab1 as (

-- SQL model to parse JSON blob stored in a single column and extract into separated field columns as described by the JSON Schema
-- depends_on: test_normalization._airbyte_raw_multiple_column_names_conflicts
select
    JSONExtractRaw(assumeNotNull(_airbyte_data), 'id') as id,
    JSONExtractRaw(assumeNotNull(_airbyte_data), 'User Id') as "User Id",
    JSONExtractRaw(assumeNotNull(_airbyte_data), 'user_id') as user_id,
    JSONExtractRaw(assumeNotNull(_airbyte_data), 'User id') as "User id",
    JSONExtractRaw(assumeNotNull(_airbyte_data), 'user id') as "user id",
    JSONExtractRaw(assumeNotNull(_airbyte_data), 'User@Id') as "User@Id",
    JSONExtractRaw(assumeNotNull(_airbyte_data), 'UserId') as UserId,
    _airbyte_ab_id,
    _airbyte_emitted_at,
    now() as _airbyte_normalized_at
from test_normalization._airbyte_raw_multiple_column_names_conflicts as table_alias
-- multiple_column_names_conflicts
where 1 = 1

),  __dbt__cte__multiple_column_names_conflicts_ab2 as (

-- SQL model to cast each column to its adequate SQL type converted from the JSON schema type
-- depends_on: __dbt__cte__multiple_column_names_conflicts_ab1
select
    accurateCastOrNull(id, '
    BIGINT
') as id,
    nullif(accurateCastOrNull(trim(BOTH '"' from "User Id"), 'String'), 'null') as "User Id",
    accurateCastOrNull(user_id, '
    Float64
') as user_id,
    accurateCastOrNull("User id", '
    Float64
') as "User id",
    accurateCastOrNull("user id", '
    Float64
') as "user id",
    nullif(accurateCastOrNull(trim(BOTH '"' from "User@Id"), 'String'), 'null') as "User@Id",
    accurateCastOrNull(UserId, '
    Float64
') as UserId,
    _airbyte_ab_id,
    _airbyte_emitted_at,
    now() as _airbyte_normalized_at
from __dbt__cte__multiple_column_names_conflicts_ab1
-- multiple_column_names_conflicts
where 1 = 1

)-- SQL model to build a hash column based on the values of this record
-- depends_on: __dbt__cte__multiple_column_names_conflicts_ab2
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
from __dbt__cte__multiple_column_names_conflicts_ab2 tmp
-- multiple_column_names_conflicts
where 1 = 1

  )