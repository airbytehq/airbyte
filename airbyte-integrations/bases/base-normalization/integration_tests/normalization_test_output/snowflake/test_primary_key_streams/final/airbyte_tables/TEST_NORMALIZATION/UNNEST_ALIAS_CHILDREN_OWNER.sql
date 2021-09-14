

      create or replace transient table "AIRBYTE_DATABASE".TEST_NORMALIZATION."UNNEST_ALIAS_CHILDREN_OWNER"  as
      (
with __dbt__CTE__UNNEST_ALIAS_CHILDREN_OWNER_AB1 as (

-- SQL model to parse JSON blob stored in a single column and extract into separated field columns as described by the JSON Schema
select
    _AIRBYTE_CHILDREN_HASHID,
    to_varchar(get_path(parse_json(OWNER), '"owner_id"')) as OWNER_ID,
    _AIRBYTE_EMITTED_AT
from "AIRBYTE_DATABASE".TEST_NORMALIZATION."UNNEST_ALIAS_CHILDREN" as table_alias
where OWNER is not null
-- OWNER at unnest_alias/children/owner
),  __dbt__CTE__UNNEST_ALIAS_CHILDREN_OWNER_AB2 as (

-- SQL model to cast each column to its adequate SQL type converted from the JSON schema type
select
    _AIRBYTE_CHILDREN_HASHID,
    cast(OWNER_ID as 
    bigint
) as OWNER_ID,
    _AIRBYTE_EMITTED_AT
from __dbt__CTE__UNNEST_ALIAS_CHILDREN_OWNER_AB1
-- OWNER at unnest_alias/children/owner
),  __dbt__CTE__UNNEST_ALIAS_CHILDREN_OWNER_AB3 as (

-- SQL model to build a hash column based on the values of this record
select
    md5(cast(
    
    coalesce(cast(_AIRBYTE_CHILDREN_HASHID as 
    varchar
), '') || '-' || coalesce(cast(OWNER_ID as 
    varchar
), '')

 as 
    varchar
)) as _AIRBYTE_OWNER_HASHID,
    tmp.*
from __dbt__CTE__UNNEST_ALIAS_CHILDREN_OWNER_AB2 tmp
-- OWNER at unnest_alias/children/owner
)-- Final base SQL model
select
    _AIRBYTE_CHILDREN_HASHID,
    OWNER_ID,
    _AIRBYTE_EMITTED_AT,
    _AIRBYTE_OWNER_HASHID
from __dbt__CTE__UNNEST_ALIAS_CHILDREN_OWNER_AB3
-- OWNER at unnest_alias/children/owner from "AIRBYTE_DATABASE".TEST_NORMALIZATION."UNNEST_ALIAS_CHILDREN"
      );
    