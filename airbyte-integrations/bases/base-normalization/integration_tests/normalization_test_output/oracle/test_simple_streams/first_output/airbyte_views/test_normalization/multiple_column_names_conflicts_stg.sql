
  create view test_normalization.multiple_column_names_conflicts_stg__dbt_tmp as
    
with dbt__cte__multiple_column_names_conflicts_ab1__ as (

-- SQL model to parse JSON blob stored in a single column and extract into separated field columns as described by the JSON Schema
-- depends_on: test_normalization.airbyte_raw_multiple_column_names_conflicts
select
    json_value("_AIRBYTE_DATA", '$."id"') as id,
    json_value("_AIRBYTE_DATA", '$."User Id"') as user_id,
    json_value("_AIRBYTE_DATA", '$."user_id"') as user_id_1,
    json_value("_AIRBYTE_DATA", '$."User id"') as user_id_2,
    json_value("_AIRBYTE_DATA", '$."user id"') as user_id_3,
    json_value("_AIRBYTE_DATA", '$."User@Id"') as user_id_4,
    json_value("_AIRBYTE_DATA", '$."UserId"') as userid,
    "_AIRBYTE_AB_ID",
    "_AIRBYTE_EMITTED_AT",
    
    CURRENT_TIMESTAMP
 as "_AIRBYTE_NORMALIZED_AT"
from test_normalization.airbyte_raw_multiple_column_names_conflicts 
-- multiple_column_names_conflicts
where 1 = 1

),  dbt__cte__multiple_column_names_conflicts_ab2__ as (

-- SQL model to cast each column to its adequate SQL type converted from the JSON schema type
-- depends_on: dbt__cte__multiple_column_names_conflicts_ab1__
select
    cast(id as 
    numeric
) as id,
    cast(user_id as varchar2(4000)) as user_id,
    cast(user_id_1 as 
    float
) as user_id_1,
    cast(user_id_2 as 
    float
) as user_id_2,
    cast(user_id_3 as 
    float
) as user_id_3,
    cast(user_id_4 as varchar2(4000)) as user_id_4,
    cast(userid as 
    float
) as userid,
    "_AIRBYTE_AB_ID",
    "_AIRBYTE_EMITTED_AT",
    
    CURRENT_TIMESTAMP
 as "_AIRBYTE_NORMALIZED_AT"
from dbt__cte__multiple_column_names_conflicts_ab1__
-- multiple_column_names_conflicts
where 1 = 1

)-- SQL model to build a hash column based on the values of this record
-- depends_on: dbt__cte__multiple_column_names_conflicts_ab2__
select
    ora_hash(
            
                id || '~' ||
            
            
                user_id || '~' ||
            
            
                user_id_1 || '~' ||
            
            
                user_id_2 || '~' ||
            
            
                user_id_3 || '~' ||
            
            
                user_id_4 || '~' ||
            
            
                userid
            
    ) as "_AIRBYTE_MULTIPLE_COLUMN_NAMES_CONFLICTS_HASHID",
    tmp.*
from dbt__cte__multiple_column_names_conflicts_ab2__ tmp
-- multiple_column_names_conflicts
where 1 = 1


