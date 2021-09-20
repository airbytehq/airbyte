

  create  table "postgres".test_normalization."unnest_alias_children__dbt_tmp"
  as (
    
with __dbt__CTE__unnest_alias_children_ab1 as (

-- SQL model to parse JSON blob stored in a single column and extract into separated field columns as described by the JSON Schema

select
    _airbyte_unnest_alias_hashid,
    jsonb_extract_path_text(_airbyte_nested_data, 'ab_id') as ab_id,
    
        jsonb_extract_path(_airbyte_nested_data, 'owner')
     as "owner",
    _airbyte_emitted_at
from "postgres".test_normalization."unnest_alias" as table_alias
cross join jsonb_array_elements(
        case jsonb_typeof(children)
        when 'array' then children
        else '[]' end
    ) as _airbyte_nested_data
where children is not null
-- children at unnest_alias/children
),  __dbt__CTE__unnest_alias_children_ab2 as (

-- SQL model to cast each column to its adequate SQL type converted from the JSON schema type
select
    _airbyte_unnest_alias_hashid,
    cast(ab_id as 
    bigint
) as ab_id,
    cast("owner" as 
    jsonb
) as "owner",
    _airbyte_emitted_at
from __dbt__CTE__unnest_alias_children_ab1
-- children at unnest_alias/children
),  __dbt__CTE__unnest_alias_children_ab3 as (

-- SQL model to build a hash column based on the values of this record
select
    md5(cast(
    
    coalesce(cast(_airbyte_unnest_alias_hashid as 
    varchar
), '') || '-' || coalesce(cast(ab_id as 
    varchar
), '') || '-' || coalesce(cast("owner" as 
    varchar
), '')

 as 
    varchar
)) as _airbyte_children_hashid,
    tmp.*
from __dbt__CTE__unnest_alias_children_ab2 tmp
-- children at unnest_alias/children
)-- Final base SQL model
select
    _airbyte_unnest_alias_hashid,
    ab_id,
    "owner",
    _airbyte_emitted_at,
    _airbyte_children_hashid
from __dbt__CTE__unnest_alias_children_ab3
-- children at unnest_alias/children from "postgres".test_normalization."unnest_alias"
  );