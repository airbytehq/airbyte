

  create  table
    test_normalization.`conflict_stream_scalar__dbt_tmp`
  as (
    
with __dbt__CTE__conflict_stream_scalar_ab1 as (

-- SQL model to parse JSON blob stored in a single column and extract into separated field columns as described by the JSON Schema
select
    json_value(_airbyte_data, 
    '$."id"') as id,
    json_value(_airbyte_data, 
    '$."conflict_stream_scalar"') as conflict_stream_scalar,
    _airbyte_emitted_at
from test_normalization._airbyte_raw_conflict_stream_scalar as table_alias
-- conflict_stream_scalar
),  __dbt__CTE__conflict_stream_scalar_ab2 as (

-- SQL model to cast each column to its adequate SQL type converted from the JSON schema type
select
    cast(id as char) as id,
    cast(conflict_stream_scalar as 
    signed
) as conflict_stream_scalar,
    _airbyte_emitted_at
from __dbt__CTE__conflict_stream_scalar_ab1
-- conflict_stream_scalar
),  __dbt__CTE__conflict_stream_scalar_ab3 as (

-- SQL model to build a hash column based on the values of this record
select
    md5(cast(concat(coalesce(cast(id as char), ''), '-', coalesce(cast(conflict_stream_scalar as char), '')) as char)) as _airbyte_conflict_stream_scalar_hashid,
    tmp.*
from __dbt__CTE__conflict_stream_scalar_ab2 tmp
-- conflict_stream_scalar
)-- Final base SQL model
select
    id,
    conflict_stream_scalar,
    _airbyte_emitted_at,
    _airbyte_conflict_stream_scalar_hashid
from __dbt__CTE__conflict_stream_scalar_ab3
-- conflict_stream_scalar from test_normalization._airbyte_raw_conflict_stream_scalar
  )
