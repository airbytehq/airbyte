

  create  table "postgres".test_normalization."unnest_alias_children_owner__dbt_tmp"
  as (
    
with __dbt__cte__unnest_alias_children_owner_ab1 as (

-- SQL model to parse JSON blob stored in a single column and extract into separated field columns as described by the JSON Schema
-- depends_on: "postgres".test_normalization."unnest_alias_children"
select
    _airbyte_children_hashid,
    jsonb_extract_path_text("owner", 'owner_id') as owner_id,
    jsonb_extract_path("owner", 'column`_''with"_quotes') as "column`_'with""_quotes",
    _airbyte_ab_id,
    _airbyte_emitted_at,
    now() as _airbyte_normalized_at
from "postgres".test_normalization."unnest_alias_children" as table_alias
-- owner at unnest_alias/children/owner
where 1 = 1
and "owner" is not null
),  __dbt__cte__unnest_alias_children_owner_ab2 as (

-- SQL model to cast each column to its adequate SQL type converted from the JSON schema type
-- depends_on: __dbt__cte__unnest_alias_children_owner_ab1
select
    _airbyte_children_hashid,
    cast(owner_id as 
    bigint
) as owner_id,
    "column`_'with""_quotes",
    _airbyte_ab_id,
    _airbyte_emitted_at,
    now() as _airbyte_normalized_at
from __dbt__cte__unnest_alias_children_owner_ab1
-- owner at unnest_alias/children/owner
where 1 = 1
),  __dbt__cte__unnest_alias_children_owner_ab3 as (

-- SQL model to build a hash column based on the values of this record
-- depends_on: __dbt__cte__unnest_alias_children_owner_ab2
select
    md5(cast(coalesce(cast(_airbyte_children_hashid as text), '') || '-' || coalesce(cast(owner_id as text), '') || '-' || coalesce(cast("column`_'with""_quotes" as text), '') as text)) as _airbyte_owner_hashid,
    tmp.*
from __dbt__cte__unnest_alias_children_owner_ab2 tmp
-- owner at unnest_alias/children/owner
where 1 = 1
)-- Final base SQL model
-- depends_on: __dbt__cte__unnest_alias_children_owner_ab3
select
    _airbyte_children_hashid,
    owner_id,
    "column`_'with""_quotes",
    _airbyte_ab_id,
    _airbyte_emitted_at,
    now() as _airbyte_normalized_at,
    _airbyte_owner_hashid
from __dbt__cte__unnest_alias_children_owner_ab3
-- owner at unnest_alias/children/owner from "postgres".test_normalization."unnest_alias_children"
where 1 = 1
  );