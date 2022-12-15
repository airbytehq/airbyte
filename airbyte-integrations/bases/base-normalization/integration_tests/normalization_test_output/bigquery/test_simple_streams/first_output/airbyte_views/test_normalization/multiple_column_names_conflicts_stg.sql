

  create or replace view `dataline-integration-testing`._airbyte_test_normalization.`multiple_column_names_conflicts_stg`
  OPTIONS()
  as 
with __dbt__cte__multiple_column_names_conflicts_ab1 as (

-- SQL model to parse JSON blob stored in a single column and extract into separated field columns as described by the JSON Schema
-- depends_on: `dataline-integration-testing`.test_normalization._airbyte_raw_multiple_column_names_conflicts
select
    json_extract_scalar(_airbyte_data, "$['id']") as id,
    json_extract_scalar(_airbyte_data, "$['User Id']") as User_Id,
    json_extract_scalar(_airbyte_data, "$['user_id']") as user_id_1,
    json_extract_scalar(_airbyte_data, "$['User id']") as User_id_2,
    json_extract_scalar(_airbyte_data, "$['user id']") as user_id_3,
    json_extract_scalar(_airbyte_data, "$['User@Id']") as User_Id_4,
    json_extract_scalar(_airbyte_data, "$['UserId']") as UserId,
    _airbyte_ab_id,
    _airbyte_emitted_at,
    CURRENT_TIMESTAMP() as _airbyte_normalized_at
from `dataline-integration-testing`.test_normalization._airbyte_raw_multiple_column_names_conflicts as table_alias
-- multiple_column_names_conflicts
where 1 = 1

),  __dbt__cte__multiple_column_names_conflicts_ab2 as (

-- SQL model to cast each column to its adequate SQL type converted from the JSON schema type
-- depends_on: __dbt__cte__multiple_column_names_conflicts_ab1
select
    cast(id as 
    int64
) as id,
    cast(User_Id as 
    string
) as User_Id,
    cast(user_id_1 as 
    float64
) as user_id_1,
    cast(User_id_2 as 
    float64
) as User_id_2,
    cast(user_id_3 as 
    float64
) as user_id_3,
    cast(User_Id_4 as 
    string
) as User_Id_4,
    cast(UserId as 
    float64
) as UserId,
    _airbyte_ab_id,
    _airbyte_emitted_at,
    CURRENT_TIMESTAMP() as _airbyte_normalized_at
from __dbt__cte__multiple_column_names_conflicts_ab1
-- multiple_column_names_conflicts
where 1 = 1

)-- SQL model to build a hash column based on the values of this record
-- depends_on: __dbt__cte__multiple_column_names_conflicts_ab2
select
    to_hex(md5(cast(concat(coalesce(cast(id as 
    string
), ''), '-', coalesce(cast(User_Id as 
    string
), ''), '-', coalesce(cast(user_id_1 as 
    string
), ''), '-', coalesce(cast(User_id_2 as 
    string
), ''), '-', coalesce(cast(user_id_3 as 
    string
), ''), '-', coalesce(cast(User_Id_4 as 
    string
), ''), '-', coalesce(cast(UserId as 
    string
), '')) as 
    string
))) as _airbyte_multiple_column_names_conflicts_hashid,
    tmp.*
from __dbt__cte__multiple_column_names_conflicts_ab2 tmp
-- multiple_column_names_conflicts
where 1 = 1
;

