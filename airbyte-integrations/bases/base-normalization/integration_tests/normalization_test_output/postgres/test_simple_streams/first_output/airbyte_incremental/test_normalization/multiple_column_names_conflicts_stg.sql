
      

  create  table "postgres"._airbyte_test_normalization."multiple_column_names_conflicts_stg"
  as (
    
with __dbt__cte__multiple_column_names_conflicts_ab1 as (

-- SQL model to parse JSON blob stored in a single column and extract into separated field columns as described by the JSON Schema
-- depends_on: "postgres".test_normalization._airbyte_raw_multiple_column_names_conflicts
select
    jsonb_extract_path_text(_airbyte_data, 'id') as "id",
    jsonb_extract_path_text(_airbyte_data, 'User Id') as "User Id",
    jsonb_extract_path_text(_airbyte_data, 'user_id') as user_id,
    jsonb_extract_path_text(_airbyte_data, 'User id') as "User id",
    jsonb_extract_path_text(_airbyte_data, 'user id') as "user id",
    jsonb_extract_path_text(_airbyte_data, 'User@Id') as "User@Id",
    jsonb_extract_path_text(_airbyte_data, 'UserId') as userid,
    _airbyte_ab_id,
    _airbyte_emitted_at,
    now() as _airbyte_normalized_at
from "postgres".test_normalization._airbyte_raw_multiple_column_names_conflicts as table_alias
-- multiple_column_names_conflicts
where 1 = 1

),  __dbt__cte__multiple_column_names_conflicts_ab2 as (

-- SQL model to cast each column to its adequate SQL type converted from the JSON schema type
-- depends_on: __dbt__cte__multiple_column_names_conflicts_ab1
select
    cast("id" as 
    bigint
) as "id",
    cast("User Id" as text) as "User Id",
    cast(user_id as 
    float
) as user_id,
    cast("User id" as 
    float
) as "User id",
    cast("user id" as 
    float
) as "user id",
    cast("User@Id" as text) as "User@Id",
    cast(userid as 
    float
) as userid,
    _airbyte_ab_id,
    _airbyte_emitted_at,
    now() as _airbyte_normalized_at
from __dbt__cte__multiple_column_names_conflicts_ab1
-- multiple_column_names_conflicts
where 1 = 1

)-- SQL model to build a hash column based on the values of this record
-- depends_on: __dbt__cte__multiple_column_names_conflicts_ab2
select
    md5(cast(coalesce(cast("id" as text), '') || '-' || coalesce(cast("User Id" as text), '') || '-' || coalesce(cast(user_id as text), '') || '-' || coalesce(cast("User id" as text), '') || '-' || coalesce(cast("user id" as text), '') || '-' || coalesce(cast("User@Id" as text), '') || '-' || coalesce(cast(userid as text), '') as text)) as _airbyte_multiple_co__ames_conflicts_hashid,
    tmp.*
from __dbt__cte__multiple_column_names_conflicts_ab2 tmp
-- multiple_column_names_conflicts
where 1 = 1

  );
  