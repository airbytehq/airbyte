

  create  table
    test_normalization.`unnest_alias__dbt_tmp`
  as (
    
with __dbt__CTE__unnest_alias_ab1 as (

-- SQL model to parse JSON blob stored in a single column and extract into separated field columns as described by the JSON Schema
select
    json_value(_airbyte_data, 
    '$."id"') as id,
    json_extract(_airbyte_data, 
    '$."children"') as children,
    _airbyte_emitted_at
from test_normalization._airbyte_raw_unnest_alias as table_alias
-- unnest_alias
),  __dbt__CTE__unnest_alias_ab2 as (

-- SQL model to cast each column to its adequate SQL type converted from the JSON schema type
select
    cast(id as 
    signed
) as id,
    children,
    _airbyte_emitted_at
from __dbt__CTE__unnest_alias_ab1
-- unnest_alias
),  __dbt__CTE__unnest_alias_ab3 as (

-- SQL model to build a hash column based on the values of this record
select
    md5(cast(concat(coalesce(cast(id as char), ''), '-', coalesce(cast(children as char), '')) as char)) as _airbyte_unnest_alias_hashid,
    tmp.*
from __dbt__CTE__unnest_alias_ab2 tmp
-- unnest_alias
)-- Final base SQL model
select
    id,
    children,
    _airbyte_emitted_at,
    _airbyte_unnest_alias_hashid
from __dbt__CTE__unnest_alias_ab3
-- unnest_alias from test_normalization._airbyte_raw_unnest_alias
  )
