

      create or replace transient table "AIRBYTE_DATABASE".TEST_NORMALIZATION."UNNEST_ALIAS_CHILDREN"  as
      (
with __dbt__CTE__UNNEST_ALIAS_CHILDREN_AB1 as (

-- SQL model to parse JSON blob stored in a single column and extract into separated field columns as described by the JSON Schema

select
    _AIRBYTE_UNNEST_ALIAS_HASHID,
    to_varchar(get_path(parse_json(CHILDREN.value), '"ab_id"')) as AB_ID,
    
        get_path(parse_json(CHILDREN.value), '"owner"')
     as OWNER,
    _AIRBYTE_EMITTED_AT
from "AIRBYTE_DATABASE".TEST_NORMALIZATION."UNNEST_ALIAS" as table_alias
cross join table(flatten(CHILDREN)) as CHILDREN
where CHILDREN is not null
-- CHILDREN at unnest_alias/children
),  __dbt__CTE__UNNEST_ALIAS_CHILDREN_AB2 as (

-- SQL model to cast each column to its adequate SQL type converted from the JSON schema type
select
    _AIRBYTE_UNNEST_ALIAS_HASHID,
    cast(AB_ID as 
    bigint
) as AB_ID,
    cast(OWNER as 
    variant
) as OWNER,
    _AIRBYTE_EMITTED_AT
from __dbt__CTE__UNNEST_ALIAS_CHILDREN_AB1
-- CHILDREN at unnest_alias/children
),  __dbt__CTE__UNNEST_ALIAS_CHILDREN_AB3 as (

-- SQL model to build a hash column based on the values of this record
select
    md5(cast(
    
    coalesce(cast(_AIRBYTE_UNNEST_ALIAS_HASHID as 
    varchar
), '') || '-' || coalesce(cast(AB_ID as 
    varchar
), '') || '-' || coalesce(cast(OWNER as 
    varchar
), '')

 as 
    varchar
)) as _AIRBYTE_CHILDREN_HASHID,
    tmp.*
from __dbt__CTE__UNNEST_ALIAS_CHILDREN_AB2 tmp
-- CHILDREN at unnest_alias/children
)-- Final base SQL model
select
    _AIRBYTE_UNNEST_ALIAS_HASHID,
    AB_ID,
    OWNER,
    _AIRBYTE_EMITTED_AT,
    _AIRBYTE_CHILDREN_HASHID
from __dbt__CTE__UNNEST_ALIAS_CHILDREN_AB3
-- CHILDREN at unnest_alias/children from "AIRBYTE_DATABASE".TEST_NORMALIZATION."UNNEST_ALIAS"
      );
    