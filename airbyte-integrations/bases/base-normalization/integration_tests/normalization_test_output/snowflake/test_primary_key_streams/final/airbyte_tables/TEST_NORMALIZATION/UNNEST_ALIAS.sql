

      create or replace transient table "AIRBYTE_DATABASE".TEST_NORMALIZATION."UNNEST_ALIAS"  as
      (
with __dbt__CTE__UNNEST_ALIAS_AB1 as (

-- SQL model to parse JSON blob stored in a single column and extract into separated field columns as described by the JSON Schema
select
    to_varchar(get_path(parse_json(_airbyte_data), '"id"')) as ID,
    get_path(parse_json(_airbyte_data), '"children"') as CHILDREN,
    _AIRBYTE_EMITTED_AT
from "AIRBYTE_DATABASE".TEST_NORMALIZATION._AIRBYTE_RAW_UNNEST_ALIAS as table_alias
-- UNNEST_ALIAS
),  __dbt__CTE__UNNEST_ALIAS_AB2 as (

-- SQL model to cast each column to its adequate SQL type converted from the JSON schema type
select
    cast(ID as 
    bigint
) as ID,
    CHILDREN,
    _AIRBYTE_EMITTED_AT
from __dbt__CTE__UNNEST_ALIAS_AB1
-- UNNEST_ALIAS
),  __dbt__CTE__UNNEST_ALIAS_AB3 as (

-- SQL model to build a hash column based on the values of this record
select
    md5(cast(
    
    coalesce(cast(ID as 
    varchar
), '') || '-' || coalesce(cast(CHILDREN as 
    varchar
), '')

 as 
    varchar
)) as _AIRBYTE_UNNEST_ALIAS_HASHID,
    tmp.*
from __dbt__CTE__UNNEST_ALIAS_AB2 tmp
-- UNNEST_ALIAS
)-- Final base SQL model
select
    ID,
    CHILDREN,
    _AIRBYTE_EMITTED_AT,
    _AIRBYTE_UNNEST_ALIAS_HASHID
from __dbt__CTE__UNNEST_ALIAS_AB3
-- UNNEST_ALIAS from "AIRBYTE_DATABASE".TEST_NORMALIZATION._AIRBYTE_RAW_UNNEST_ALIAS
      );
    