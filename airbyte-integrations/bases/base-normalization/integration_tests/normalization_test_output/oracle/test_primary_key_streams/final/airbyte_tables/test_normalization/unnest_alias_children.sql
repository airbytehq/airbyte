

  create  table test_normalization.unnest_alias_children__dbt_tmp
  
  as
    
with dbt__cte__unnest_alias_children_ab1__ as (

-- SQL model to parse JSON blob stored in a single column and extract into separated field columns as described by the JSON Schema

select
    "_AIRBYTE_UNNEST_ALIAS_HASHID",
    json_value(children, '$."ab_id"') as ab_id,
    json_value(children, '$."owner"') as owner,
    "_AIRBYTE_EMITTED_AT"
from test_normalization.unnest_alias 

where children is not null
-- children at unnest_alias/children
),  dbt__cte__unnest_alias_children_ab2__ as (

-- SQL model to cast each column to its adequate SQL type converted from the JSON schema type
select
    "_AIRBYTE_UNNEST_ALIAS_HASHID",
    cast(ab_id as 
    numeric
) as ab_id,
    cast(owner as varchar2(4000)) as owner,
    "_AIRBYTE_EMITTED_AT"
from dbt__cte__unnest_alias_children_ab1__
-- children at unnest_alias/children
),  dbt__cte__unnest_alias_children_ab3__ as (

-- SQL model to build a hash column based on the values of this record
select
    ora_hash(
            
                "_AIRBYTE_UNNEST_ALIAS_HASHID" || '~' ||
            
            
                ab_id || '~' ||
            
            
                owner
            
    ) as "_AIRBYTE_CHILDREN_HASHID",
    tmp.*
from dbt__cte__unnest_alias_children_ab2__ tmp
-- children at unnest_alias/children
)-- Final base SQL model
select
    "_AIRBYTE_UNNEST_ALIAS_HASHID",
    ab_id,
    owner,
    "_AIRBYTE_EMITTED_AT",
    "_AIRBYTE_CHILDREN_HASHID"
from dbt__cte__unnest_alias_children_ab3__
-- children at unnest_alias/children from test_normalization.unnest_alias