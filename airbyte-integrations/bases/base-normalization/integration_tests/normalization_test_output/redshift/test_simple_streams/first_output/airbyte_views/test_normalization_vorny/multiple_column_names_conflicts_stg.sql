

  create view "normalization_tests"._airbyte_test_normalization_vorny."multiple_column_names_conflicts_stg__dbt_tmp" as (
    
with __dbt__cte__multiple_column_names_conflicts_ab1 as (

-- SQL model to parse JSON blob stored in a single column and extract into separated field columns as described by the JSON Schema
-- depends_on: "normalization_tests".test_normalization_vorny._airbyte_raw_multiple_column_names_conflicts
select
    case when _airbyte_data."id" != '' then _airbyte_data."id" end as id,
    case when _airbyte_data."User Id" != '' then _airbyte_data."User Id" end as "user id",
    case when _airbyte_data."user_id" != '' then _airbyte_data."user_id" end as user_id,
    case when _airbyte_data."User id" != '' then _airbyte_data."User id" end as "user id_1",
    case when _airbyte_data."user id" != '' then _airbyte_data."user id" end as "user id_2",
    case when _airbyte_data."User@Id" != '' then _airbyte_data."User@Id" end as "user@id",
    case when _airbyte_data."UserId" != '' then _airbyte_data."UserId" end as userid,
    _airbyte_ab_id,
    _airbyte_emitted_at,
    getdate() as _airbyte_normalized_at
from "normalization_tests".test_normalization_vorny._airbyte_raw_multiple_column_names_conflicts as table_alias
-- multiple_column_names_conflicts
where 1 = 1

),  __dbt__cte__multiple_column_names_conflicts_ab2 as (

-- SQL model to cast each column to its adequate SQL type converted from the JSON schema type
-- depends_on: __dbt__cte__multiple_column_names_conflicts_ab1
select
    cast(id as 
    bigint
) as id,
    cast("user id" as text) as "user id",
    cast(user_id as 
    float
) as user_id,
    cast("user id_1" as 
    float
) as "user id_1",
    cast("user id_2" as 
    float
) as "user id_2",
    cast("user@id" as text) as "user@id",
    cast(userid as 
    float
) as userid,
    _airbyte_ab_id,
    _airbyte_emitted_at,
    getdate() as _airbyte_normalized_at
from __dbt__cte__multiple_column_names_conflicts_ab1
-- multiple_column_names_conflicts
where 1 = 1

)-- SQL model to build a hash column based on the values of this record
-- depends_on: __dbt__cte__multiple_column_names_conflicts_ab2
select
    md5(cast(coalesce(cast(id as text), '') || '-' || coalesce(cast("user id" as text), '') || '-' || coalesce(cast(user_id as text), '') || '-' || coalesce(cast("user id_1" as text), '') || '-' || coalesce(cast("user id_2" as text), '') || '-' || coalesce(cast("user@id" as text), '') || '-' || coalesce(cast(userid as text), '') as text)) as _airbyte_multiple_column_names_conflicts_hashid,
    tmp.*
from __dbt__cte__multiple_column_names_conflicts_ab2 tmp
-- multiple_column_names_conflicts
where 1 = 1

  ) ;
