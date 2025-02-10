

  create  table "postgres".test_normalization."unnest_alias__dbt_tmp"
  as (
    
with __dbt__cte__unnest_alias_ab1 as (

-- SQL model to parse JSON blob stored in a single column and extract into separated field columns as described by the JSON Schema
-- depends_on: "postgres".test_normalization._airbyte_raw_unnest_alias
select
    jsonb_extract_path_text(_airbyte_data, 'id') as "id",
    jsonb_extract_path(_airbyte_data, 'children') as children,
    _airbyte_ab_id,
    _airbyte_emitted_at,
    now() as _airbyte_normalized_at
from "postgres".test_normalization._airbyte_raw_unnest_alias as table_alias
-- unnest_alias
where 1 = 1
),  __dbt__cte__unnest_alias_ab2 as (

-- SQL model to cast each column to its adequate SQL type converted from the JSON schema type
-- depends_on: __dbt__cte__unnest_alias_ab1
select
    cast("id" as 
    bigint
) as "id",
    children,
    _airbyte_ab_id,
    _airbyte_emitted_at,
    now() as _airbyte_normalized_at
from __dbt__cte__unnest_alias_ab1
-- unnest_alias
where 1 = 1
),  __dbt__cte__unnest_alias_ab3 as (

-- SQL model to build a hash column based on the values of this record
-- depends_on: __dbt__cte__unnest_alias_ab2
select
    md5(cast(coalesce(cast("id" as text), '') || '-' || coalesce(cast(children as text), '') as text)) as _airbyte_unnest_alias_hashid,
    tmp.*
from __dbt__cte__unnest_alias_ab2 tmp
-- unnest_alias
where 1 = 1
)-- Final base SQL model
-- depends_on: __dbt__cte__unnest_alias_ab3
select
    "id",
    children,
    _airbyte_ab_id,
    _airbyte_emitted_at,
    now() as _airbyte_normalized_at,
    _airbyte_unnest_alias_hashid
from __dbt__cte__unnest_alias_ab3
-- unnest_alias from "postgres".test_normalization._airbyte_raw_unnest_alias
where 1 = 1
  );