

  create  table test_normalization.unnest_alias_children_owner__dbt_tmp
  
  as
    
with dbt__cte__unnest_alias_children_owner_ab1__ as (

-- SQL model to parse JSON blob stored in a single column and extract into separated field columns as described by the JSON Schema
select
    "_AIRBYTE_CHILDREN_HASHID",
    json_value(owner, '$."owner_id"') as owner_id,
    "_AIRBYTE_EMITTED_AT"
from test_normalization.unnest_alias_children 
where owner is not null
-- owner at unnest_alias/children/owner
),  dbt__cte__unnest_alias_children_owner_ab2__ as (

-- SQL model to cast each column to its adequate SQL type converted from the JSON schema type
select
    "_AIRBYTE_CHILDREN_HASHID",
    cast(owner_id as 
    numeric
) as owner_id,
    "_AIRBYTE_EMITTED_AT"
from dbt__cte__unnest_alias_children_owner_ab1__
-- owner at unnest_alias/children/owner
),  dbt__cte__unnest_alias_children_owner_ab3__ as (

-- SQL model to build a hash column based on the values of this record
select
    ora_hash(
            
                "_AIRBYTE_CHILDREN_HASHID" || '~' ||
            
            
                owner_id
            
    ) as "_AIRBYTE_OWNER_HASHID",
    tmp.*
from dbt__cte__unnest_alias_children_owner_ab2__ tmp
-- owner at unnest_alias/children/owner
)-- Final base SQL model
select
    "_AIRBYTE_CHILDREN_HASHID",
    owner_id,
    "_AIRBYTE_EMITTED_AT",
    "_AIRBYTE_OWNER_HASHID"
from dbt__cte__unnest_alias_children_owner_ab3__
-- owner at unnest_alias/children/owner from test_normalization.unnest_alias_children