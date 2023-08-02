

  create  table "postgres".test_normalization."unnest_alias_children__dbt_tmp"
  as (
    
with __dbt__cte__unnest_alias_children_ab1 as (

-- SQL model to parse JSON blob stored in a single column and extract into separated field columns as described by the JSON Schema
-- depends_on: "postgres".test_normalization."unnest_alias"

select
    _airbyte_unnest_alias_hashid,
    jsonb_extract_path_text(_airbyte_nested_data, 'ab_id') as ab_id,
    
        jsonb_extract_path(_airbyte_nested_data, 'owner')
     as "owner",
    _airbyte_ab_id,
    _airbyte_emitted_at,
    now() as _airbyte_normalized_at
from "postgres".test_normalization."unnest_alias" as table_alias
-- children at unnest_alias/children
cross join jsonb_array_elements(
        case jsonb_typeof(children)
        when 'array' then children
        else '[]' end
    ) as _airbyte_nested_data
where 1 = 1
and children is not null
),  __dbt__cte__unnest_alias_children_ab2 as (

-- SQL model to cast each column to its adequate SQL type converted from the JSON schema type
-- depends_on: __dbt__cte__unnest_alias_children_ab1
select
    _airbyte_unnest_alias_hashid,
    cast(ab_id as 
    bigint
) as ab_id,
    cast("owner" as 
    jsonb
) as "owner",
    _airbyte_ab_id,
    _airbyte_emitted_at,
    now() as _airbyte_normalized_at
from __dbt__cte__unnest_alias_children_ab1
-- children at unnest_alias/children
where 1 = 1
),  __dbt__cte__unnest_alias_children_ab3 as (

-- SQL model to build a hash column based on the values of this record
-- depends_on: __dbt__cte__unnest_alias_children_ab2
select
    md5(cast(coalesce(cast(_airbyte_unnest_alias_hashid as text), '') || '-' || coalesce(cast(ab_id as text), '') || '-' || coalesce(cast("owner" as text), '') as text)) as _airbyte_children_hashid,
    tmp.*
from __dbt__cte__unnest_alias_children_ab2 tmp
-- children at unnest_alias/children
where 1 = 1
)-- Final base SQL model
-- depends_on: __dbt__cte__unnest_alias_children_ab3
select
    _airbyte_unnest_alias_hashid,
    ab_id,
    "owner",
    _airbyte_ab_id,
    _airbyte_emitted_at,
    now() as _airbyte_normalized_at,
    _airbyte_children_hashid
from __dbt__cte__unnest_alias_children_ab3
-- children at unnest_alias/children from "postgres".test_normalization."unnest_alias"
where 1 = 1
  );