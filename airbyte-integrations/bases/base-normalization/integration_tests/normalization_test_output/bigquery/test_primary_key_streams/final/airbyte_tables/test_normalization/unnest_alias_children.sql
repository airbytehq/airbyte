

  create or replace table `dataline-integration-testing`.test_normalization.`unnest_alias_children`
  
  
  OPTIONS()
  as (
    
with __dbt__CTE__unnest_alias_children_ab1 as (

-- SQL model to parse JSON blob stored in a single column and extract into separated field columns as described by the JSON Schema

select
    _airbyte_unnest_alias_hashid,
    json_extract_scalar(children, "$['ab_id']") as ab_id,
    
        json_extract(children, "$['owner']")
     as owner,
    _airbyte_emitted_at
from `dataline-integration-testing`.test_normalization.`unnest_alias` as table_alias
cross join unnest(children) as children
where children is not null
-- children at unnest_alias/children
),  __dbt__CTE__unnest_alias_children_ab2 as (

-- SQL model to cast each column to its adequate SQL type converted from the JSON schema type
select
    _airbyte_unnest_alias_hashid,
    cast(ab_id as 
    int64
) as ab_id,
    cast(owner as 
    string
) as owner,
    _airbyte_emitted_at
from __dbt__CTE__unnest_alias_children_ab1
-- children at unnest_alias/children
),  __dbt__CTE__unnest_alias_children_ab3 as (

-- SQL model to build a hash column based on the values of this record
select
    to_hex(md5(cast(concat(coalesce(cast(_airbyte_unnest_alias_hashid as 
    string
), ''), '-', coalesce(cast(ab_id as 
    string
), ''), '-', coalesce(cast(owner as 
    string
), '')) as 
    string
))) as _airbyte_children_hashid,
    tmp.*
from __dbt__CTE__unnest_alias_children_ab2 tmp
-- children at unnest_alias/children
)-- Final base SQL model
select
    _airbyte_unnest_alias_hashid,
    ab_id,
    owner,
    _airbyte_emitted_at,
    _airbyte_children_hashid
from __dbt__CTE__unnest_alias_children_ab3
-- children at unnest_alias/children from `dataline-integration-testing`.test_normalization.`unnest_alias`
  );
    