

  create  table
    test_normalization.`unnest_alias_children_owner__dbt_tmp`
  as (
    
with __dbt__CTE__unnest_alias_children_owner_ab1 as (

-- SQL model to parse JSON blob stored in a single column and extract into separated field columns as described by the JSON Schema
select
    _airbyte_children_hashid,
    json_value(`owner`, 
    '$."owner_id"') as owner_id,
    _airbyte_emitted_at
from test_normalization.`unnest_alias_children` as table_alias
where `owner` is not null
-- owner at unnest_alias/children/owner
),  __dbt__CTE__unnest_alias_children_owner_ab2 as (

-- SQL model to cast each column to its adequate SQL type converted from the JSON schema type
select
    _airbyte_children_hashid,
    cast(owner_id as 
    signed
) as owner_id,
    _airbyte_emitted_at
from __dbt__CTE__unnest_alias_children_owner_ab1
-- owner at unnest_alias/children/owner
),  __dbt__CTE__unnest_alias_children_owner_ab3 as (

-- SQL model to build a hash column based on the values of this record
select
    md5(cast(concat(coalesce(cast(_airbyte_children_hashid as char), ''), '-', coalesce(cast(owner_id as char), '')) as char)) as _airbyte_owner_hashid,
    tmp.*
from __dbt__CTE__unnest_alias_children_owner_ab2 tmp
-- owner at unnest_alias/children/owner
)-- Final base SQL model
select
    _airbyte_children_hashid,
    owner_id,
    _airbyte_emitted_at,
    _airbyte_owner_hashid
from __dbt__CTE__unnest_alias_children_owner_ab3
-- owner at unnest_alias/children/owner from test_normalization.`unnest_alias_children`
  )
