

  create  table "postgres".test_normalization."conflict_stream_array__dbt_tmp"
  as (
    
with __dbt__CTE__conflict_stream_array_ab1 as (

-- SQL model to parse JSON blob stored in a single column and extract into separated field columns as described by the JSON Schema
select
    jsonb_extract_path_text(_airbyte_data, 'id') as "id",
    jsonb_extract_path(_airbyte_data, 'conflict_stream_array') as conflict_stream_array,
    _airbyte_emitted_at
from "postgres".test_normalization._airbyte_raw_conflict_stream_array as table_alias
-- conflict_stream_array
),  __dbt__CTE__conflict_stream_array_ab2 as (

-- SQL model to cast each column to its adequate SQL type converted from the JSON schema type
select
    cast("id" as 
    varchar
) as "id",
    conflict_stream_array,
    _airbyte_emitted_at
from __dbt__CTE__conflict_stream_array_ab1
-- conflict_stream_array
),  __dbt__CTE__conflict_stream_array_ab3 as (

-- SQL model to build a hash column based on the values of this record
select
    md5(cast(
    
    coalesce(cast("id" as 
    varchar
), '') || '-' || coalesce(cast(conflict_stream_array as 
    varchar
), '')

 as 
    varchar
)) as _airbyte_conflict_stream_array_hashid,
    tmp.*
from __dbt__CTE__conflict_stream_array_ab2 tmp
-- conflict_stream_array
)-- Final base SQL model
select
    "id",
    conflict_stream_array,
    _airbyte_emitted_at,
    _airbyte_conflict_stream_array_hashid
from __dbt__CTE__conflict_stream_array_ab3
-- conflict_stream_array from "postgres".test_normalization._airbyte_raw_conflict_stream_array
  );