
  create or replace  view "INTEGRATION_TEST_NORMALIZATION"._AIRBYTE_TEST_NORMALIZATION."MULTIPLE_COLUMN_NAMES_CONFLICTS_STG" 
  
   as (
    
with __dbt__cte__MULTIPLE_COLUMN_NAMES_CONFLICTS_AB1 as (

-- SQL model to parse JSON blob stored in a single column and extract into separated field columns as described by the JSON Schema
-- depends_on: "INTEGRATION_TEST_NORMALIZATION".TEST_NORMALIZATION._AIRBYTE_RAW_MULTIPLE_COLUMN_NAMES_CONFLICTS
select
    to_varchar(get_path(parse_json(_airbyte_data), '"id"')) as ID,
    to_varchar(get_path(parse_json(_airbyte_data), '"User Id"')) as "User Id",
    to_varchar(get_path(parse_json(_airbyte_data), '"user_id"')) as USER_ID,
    to_varchar(get_path(parse_json(_airbyte_data), '"User id"')) as "User id",
    to_varchar(get_path(parse_json(_airbyte_data), '"user id"')) as "user id",
    to_varchar(get_path(parse_json(_airbyte_data), '"User@Id"')) as "User@Id",
    to_varchar(get_path(parse_json(_airbyte_data), '"UserId"')) as USERID,
    _AIRBYTE_AB_ID,
    _AIRBYTE_EMITTED_AT,
    convert_timezone('UTC', current_timestamp()) as _AIRBYTE_NORMALIZED_AT
from "INTEGRATION_TEST_NORMALIZATION".TEST_NORMALIZATION._AIRBYTE_RAW_MULTIPLE_COLUMN_NAMES_CONFLICTS as table_alias
-- MULTIPLE_COLUMN_NAMES_CONFLICTS
where 1 = 1

),  __dbt__cte__MULTIPLE_COLUMN_NAMES_CONFLICTS_AB2 as (

-- SQL model to cast each column to its adequate SQL type converted from the JSON schema type
-- depends_on: __dbt__cte__MULTIPLE_COLUMN_NAMES_CONFLICTS_AB1
select
    cast(ID as 
    bigint
) as ID,
    cast("User Id" as 
    varchar
) as "User Id",
    cast(USER_ID as 
    float
) as USER_ID,
    cast("User id" as 
    float
) as "User id",
    cast("user id" as 
    float
) as "user id",
    cast("User@Id" as 
    varchar
) as "User@Id",
    cast(USERID as 
    float
) as USERID,
    _AIRBYTE_AB_ID,
    _AIRBYTE_EMITTED_AT,
    convert_timezone('UTC', current_timestamp()) as _AIRBYTE_NORMALIZED_AT
from __dbt__cte__MULTIPLE_COLUMN_NAMES_CONFLICTS_AB1
-- MULTIPLE_COLUMN_NAMES_CONFLICTS
where 1 = 1

)-- SQL model to build a hash column based on the values of this record
-- depends_on: __dbt__cte__MULTIPLE_COLUMN_NAMES_CONFLICTS_AB2
select
    md5(cast(coalesce(cast(ID as 
    varchar
), '') || '-' || coalesce(cast("User Id" as 
    varchar
), '') || '-' || coalesce(cast(USER_ID as 
    varchar
), '') || '-' || coalesce(cast("User id" as 
    varchar
), '') || '-' || coalesce(cast("user id" as 
    varchar
), '') || '-' || coalesce(cast("User@Id" as 
    varchar
), '') || '-' || coalesce(cast(USERID as 
    varchar
), '') as 
    varchar
)) as _AIRBYTE_MULTIPLE_COLUMN_NAMES_CONFLICTS_HASHID,
    tmp.*
from __dbt__cte__MULTIPLE_COLUMN_NAMES_CONFLICTS_AB2 tmp
-- MULTIPLE_COLUMN_NAMES_CONFLICTS
where 1 = 1

  );
