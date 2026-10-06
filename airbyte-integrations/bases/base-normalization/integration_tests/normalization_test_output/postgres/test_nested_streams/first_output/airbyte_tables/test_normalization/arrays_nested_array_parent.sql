

  create  table "postgres".test_normalization."arrays_nested_array_parent__dbt_tmp"
  as (
    
with __dbt__cte__arrays_nested_array_parent_ab1 as (

-- SQL model to parse JSON blob stored in a single column and extract into separated field columns as described by the JSON Schema
-- depends_on: "postgres".test_normalization."arrays"
select
    _airbyte_arrays_hashid,
    jsonb_extract_path(nested_array_parent, 'nested_array') as nested_array,
    _airbyte_ab_id,
    _airbyte_emitted_at,
    now() as _airbyte_normalized_at
from "postgres".test_normalization."arrays" as table_alias
-- nested_array_parent at arrays/nested_array_parent
where 1 = 1
and nested_array_parent is not null
),  __dbt__cte__arrays_nested_array_parent_ab2 as (

-- SQL model to cast each column to its adequate SQL type converted from the JSON schema type
-- depends_on: __dbt__cte__arrays_nested_array_parent_ab1
select
    _airbyte_arrays_hashid,
    nested_array,
    _airbyte_ab_id,
    _airbyte_emitted_at,
    now() as _airbyte_normalized_at
from __dbt__cte__arrays_nested_array_parent_ab1
-- nested_array_parent at arrays/nested_array_parent
where 1 = 1
),  __dbt__cte__arrays_nested_array_parent_ab3 as (

-- SQL model to build a hash column based on the values of this record
-- depends_on: __dbt__cte__arrays_nested_array_parent_ab2
select
    md5(cast(coalesce(cast(_airbyte_arrays_hashid as text), '') || '-' || coalesce(cast(nested_array as text), '') as text)) as _airbyte_nested_array_parent_hashid,
    tmp.*
from __dbt__cte__arrays_nested_array_parent_ab2 tmp
-- nested_array_parent at arrays/nested_array_parent
where 1 = 1
)-- Final base SQL model
-- depends_on: __dbt__cte__arrays_nested_array_parent_ab3
select
    _airbyte_arrays_hashid,
    nested_array,
    _airbyte_ab_id,
    _airbyte_emitted_at,
    now() as _airbyte_normalized_at,
    _airbyte_nested_array_parent_hashid
from __dbt__cte__arrays_nested_array_parent_ab3
-- nested_array_parent at arrays/nested_array_parent from "postgres".test_normalization."arrays"
where 1 = 1
  );