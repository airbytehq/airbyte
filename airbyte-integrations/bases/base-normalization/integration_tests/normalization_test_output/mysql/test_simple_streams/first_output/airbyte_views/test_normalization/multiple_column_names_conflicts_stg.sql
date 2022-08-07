
  create view _airbyte_test_normalization.`multiple_column_names_conflicts_stg__dbt_tmp` as (
    
with __dbt__cte__multiple_column_names_conflicts_ab1 as (

-- SQL model to parse JSON blob stored in a single column and extract into separated field columns as described by the JSON Schema
-- depends_on: test_normalization._airbyte_raw_multiple_column_names_conflicts
select
    json_value(_airbyte_data, 
    '$."id"' RETURNING CHAR) as id,
    json_value(_airbyte_data, 
    '$."User Id"' RETURNING CHAR) as `User Id`,
    json_value(_airbyte_data, 
    '$."user_id"' RETURNING CHAR) as user_id,
    json_value(_airbyte_data, 
    '$."User id"' RETURNING CHAR) as `User id_1`,
    json_value(_airbyte_data, 
    '$."user id"' RETURNING CHAR) as `user id_2`,
    json_value(_airbyte_data, 
    '$."User@Id"' RETURNING CHAR) as `User@Id`,
    json_value(_airbyte_data, 
    '$."UserId"' RETURNING CHAR) as userid,
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
    signed
) as id,
    cast(`User Id` as char(1024)) as `User Id`,
    cast(user_id as 
    float
) as user_id,
    cast(`User id_1` as 
    float
) as `User id_1`,
    cast(`user id_2` as 
    float
) as `user id_2`,
    cast(`User@Id` as char(1024)) as `User@Id`,
    cast(userid as 
    float
) as userid,
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
    md5(cast(concat(coalesce(cast(id as char), ''), '-', coalesce(cast(`User Id` as char), ''), '-', coalesce(cast(user_id as char), ''), '-', coalesce(cast(`User id_1` as char), ''), '-', coalesce(cast(`user id_2` as char), ''), '-', coalesce(cast(`User@Id` as char), ''), '-', coalesce(cast(userid as char), '')) as char)) as _airbyte_multiple_col__ames_conflicts_hashid,
    tmp.*
from __dbt__cte__multiple_column_names_conflicts_ab2 tmp
-- multiple_column_names_conflicts
where 1 = 1

  );