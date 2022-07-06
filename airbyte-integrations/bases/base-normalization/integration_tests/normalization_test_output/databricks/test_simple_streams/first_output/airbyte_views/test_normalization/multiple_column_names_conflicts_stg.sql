create or replace view _airbyte_test_normalization.`multiple_column_names_conflicts_stg`
  
  as
    
with __dbt__cte__multiple_column_names_conflicts_ab1 as (

-- SQL model to parse JSON blob stored in a single column and extract into separated field columns as described by the JSON Schema
-- depends_on: test_normalization._airbyte_raw_multiple_column_names_conflicts
select
    get_json_object(_airbyte_data, '$.id') as id,
    get_json_object(_airbyte_data, '$.User Id') as User_Id,
    get_json_object(_airbyte_data, '$.user_id') as user_id_1,
    get_json_object(_airbyte_data, '$.User id') as User_id_2,
    get_json_object(_airbyte_data, '$.user id') as user_id_3,
    get_json_object(_airbyte_data, '$.User@Id') as User_Id_4,
    get_json_object(_airbyte_data, '$.UserId') as UserId,
    _airbyte_ab_id,
    _airbyte_emitted_at,
    
    CURRENT_TIMESTAMP
 as _airbyte_normalized_at
from test_normalization._airbyte_raw_multiple_column_names_conflicts as table_alias
-- multiple_column_names_conflicts
where 1 = 1

),  __dbt__cte__multiple_column_names_conflicts_ab2 as (

-- SQL model to cast each column to its adequate SQL type converted from the JSON schema type
-- depends_on: __dbt__cte__multiple_column_names_conflicts_ab1
select
    cast(id as 
    BIGINT
) as id,
    cast(User_Id as 
    string
) as User_Id,
    cast(user_id_1 as 
    float
) as user_id_1,
    cast(User_id_2 as 
    float
) as User_id_2,
    cast(user_id_3 as 
    float
) as user_id_3,
    cast(User_Id_4 as 
    string
) as User_Id_4,
    cast(UserId as 
    float
) as UserId,
    _airbyte_ab_id,
    _airbyte_emitted_at,
    
    CURRENT_TIMESTAMP
 as _airbyte_normalized_at
from __dbt__cte__multiple_column_names_conflicts_ab1
-- multiple_column_names_conflicts
where 1 = 1

)-- SQL model to build a hash column based on the values of this record
-- depends_on: __dbt__cte__multiple_column_names_conflicts_ab2
select
    md5(cast(coalesce(cast(id as 
    string
), '') || '-' || coalesce(cast(User_Id as 
    string
), '') || '-' || coalesce(cast(user_id_1 as 
    string
), '') || '-' || coalesce(cast(User_id_2 as 
    string
), '') || '-' || coalesce(cast(user_id_3 as 
    string
), '') || '-' || coalesce(cast(User_Id_4 as 
    string
), '') || '-' || coalesce(cast(UserId as 
    string
), '') as 
    string
)) as _airbyte_multiple_column_names_conflicts_hashid,
    tmp.*
from __dbt__cte__multiple_column_names_conflicts_ab2 tmp
-- multiple_column_names_conflicts
where 1 = 1

