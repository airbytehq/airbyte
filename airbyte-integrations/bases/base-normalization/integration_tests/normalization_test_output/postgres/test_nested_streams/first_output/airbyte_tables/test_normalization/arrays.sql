

  create  table "postgres".test_normalization."arrays__dbt_tmp"
  as (
    
with __dbt__cte__arrays_ab1 as (

-- SQL model to parse JSON blob stored in a single column and extract into separated field columns as described by the JSON Schema
-- depends_on: "postgres".test_normalization._airbyte_raw_arrays
select
    jsonb_extract_path(_airbyte_data, 'array_of_strings') as array_of_strings,
    
        jsonb_extract_path(table_alias._airbyte_data, 'nested_array_parent')
     as nested_array_parent,
    _airbyte_ab_id,
    _airbyte_emitted_at,
    now() as _airbyte_normalized_at
from "postgres".test_normalization._airbyte_raw_arrays as table_alias
-- arrays
where 1 = 1
),  __dbt__cte__arrays_ab2 as (

-- SQL model to cast each column to its adequate SQL type converted from the JSON schema type
-- depends_on: __dbt__cte__arrays_ab1
select
    array_of_strings,
    cast(nested_array_parent as 
    jsonb
) as nested_array_parent,
    _airbyte_ab_id,
    _airbyte_emitted_at,
    now() as _airbyte_normalized_at
from __dbt__cte__arrays_ab1
-- arrays
where 1 = 1
),  __dbt__cte__arrays_ab3 as (

-- SQL model to build a hash column based on the values of this record
-- depends_on: __dbt__cte__arrays_ab2
select
    md5(cast(coalesce(cast(array_of_strings as text), '') || '-' || coalesce(cast(nested_array_parent as text), '') as text)) as _airbyte_arrays_hashid,
    tmp.*
from __dbt__cte__arrays_ab2 tmp
-- arrays
where 1 = 1
)-- Final base SQL model
-- depends_on: __dbt__cte__arrays_ab3
select
    array_of_strings,
    nested_array_parent,
    _airbyte_ab_id,
    _airbyte_emitted_at,
    now() as _airbyte_normalized_at,
    _airbyte_arrays_hashid
from __dbt__cte__arrays_ab3
-- arrays from "postgres".test_normalization._airbyte_raw_arrays
where 1 = 1
  );