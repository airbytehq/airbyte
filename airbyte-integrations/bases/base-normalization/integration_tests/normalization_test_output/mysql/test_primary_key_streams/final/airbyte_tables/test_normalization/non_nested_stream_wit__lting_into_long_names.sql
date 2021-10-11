

  create  table
    test_normalization.`non_nested_stream_wit__lting_into_long_names__dbt_tmp`
  as (
    
with __dbt__CTE__non_nested_stream_wit_1g_into_long_names_ab1 as (

-- SQL model to parse JSON blob stored in a single column and extract into separated field columns as described by the JSON Schema
select
    json_value(_airbyte_data, 
    '$."id"') as id,
    json_value(_airbyte_data, 
    '$."date"') as `date`,
    _airbyte_emitted_at
from test_normalization._airbyte_raw_non_nest__lting_into_long_names as table_alias
-- non_nested_stream_wit__lting_into_long_names
),  __dbt__CTE__non_nested_stream_wit_1g_into_long_names_ab2 as (

-- SQL model to cast each column to its adequate SQL type converted from the JSON schema type
select
    cast(id as char) as id,
    cast(`date` as char) as `date`,
    _airbyte_emitted_at
from __dbt__CTE__non_nested_stream_wit_1g_into_long_names_ab1
-- non_nested_stream_wit__lting_into_long_names
),  __dbt__CTE__non_nested_stream_wit_1g_into_long_names_ab3 as (

-- SQL model to build a hash column based on the values of this record
select
    md5(cast(concat(coalesce(cast(id as char), ''), '-', coalesce(cast(`date` as char), '')) as char)) as _airbyte_non_nested_s__nto_long_names_hashid,
    tmp.*
from __dbt__CTE__non_nested_stream_wit_1g_into_long_names_ab2 tmp
-- non_nested_stream_wit__lting_into_long_names
)-- Final base SQL model
select
    id,
    `date`,
    _airbyte_emitted_at,
    _airbyte_non_nested_s__nto_long_names_hashid
from __dbt__CTE__non_nested_stream_wit_1g_into_long_names_ab3
-- non_nested_stream_wit__lting_into_long_names from test_normalization._airbyte_raw_non_nest__lting_into_long_names
  )
