

  create  table
    test_normalization.`conflict_stream_name_conflict_stream_name__dbt_tmp`
  as (
    
with __dbt__CTE__conflict_stream_name__2flict_stream_name_ab1 as (

-- SQL model to parse JSON blob stored in a single column and extract into separated field columns as described by the JSON Schema
select
    _airbyte_conflict_stream_name_hashid,
    
        json_extract(table_alias.conflict_stream_name, 
    '$."conflict_stream_name"')
     as conflict_stream_name,
    _airbyte_emitted_at
from test_normalization.`conflict_stream_name` as table_alias
where conflict_stream_name is not null
-- conflict_stream_name at conflict_stream_name/conflict_stream_name
),  __dbt__CTE__conflict_stream_name__2flict_stream_name_ab2 as (

-- SQL model to cast each column to its adequate SQL type converted from the JSON schema type
select
    _airbyte_conflict_stream_name_hashid,
    cast(conflict_stream_name as json) as conflict_stream_name,
    _airbyte_emitted_at
from __dbt__CTE__conflict_stream_name__2flict_stream_name_ab1
-- conflict_stream_name at conflict_stream_name/conflict_stream_name
),  __dbt__CTE__conflict_stream_name__2flict_stream_name_ab3 as (

-- SQL model to build a hash column based on the values of this record
select
    md5(cast(concat(coalesce(cast(_airbyte_conflict_stream_name_hashid as char), ''), '-', coalesce(cast(conflict_stream_name as char), '')) as char)) as _airbyte_conflict_stream_name_2_hashid,
    tmp.*
from __dbt__CTE__conflict_stream_name__2flict_stream_name_ab2 tmp
-- conflict_stream_name at conflict_stream_name/conflict_stream_name
)-- Final base SQL model
select
    _airbyte_conflict_stream_name_hashid,
    conflict_stream_name,
    _airbyte_emitted_at,
    _airbyte_conflict_stream_name_2_hashid
from __dbt__CTE__conflict_stream_name__2flict_stream_name_ab3
-- conflict_stream_name at conflict_stream_name/conflict_stream_name from test_normalization.`conflict_stream_name`
  )
