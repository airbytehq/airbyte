

  create  table
    "integrationtests".test_normalization."conflict_stream_array_conflict_stream_array__dbt_tmp"
    
    
  as (
    
with __dbt__CTE__conflict_stream_array_conflict_stream_array_ab1 as (

-- SQL model to parse JSON blob stored in a single column and extract into separated field columns as described by the JSON Schema
select
    _airbyte_conflict_stream_array_hashid,
    json_extract_path_text(conflict_stream_array, 'conflict_stream_name', true) as conflict_stream_name,
    _airbyte_emitted_at
from "integrationtests".test_normalization."conflict_stream_array" as table_alias
where conflict_stream_array is not null
-- conflict_stream_array at conflict_stream_array/conflict_stream_array
),  __dbt__CTE__conflict_stream_array_conflict_stream_array_ab2 as (

-- SQL model to cast each column to its adequate SQL type converted from the JSON schema type
select
    _airbyte_conflict_stream_array_hashid,
    conflict_stream_name,
    _airbyte_emitted_at
from __dbt__CTE__conflict_stream_array_conflict_stream_array_ab1
-- conflict_stream_array at conflict_stream_array/conflict_stream_array
),  __dbt__CTE__conflict_stream_array_conflict_stream_array_ab3 as (

-- SQL model to build a hash column based on the values of this record
select
    *,
    md5(cast(
    
    coalesce(cast(_airbyte_conflict_stream_array_hashid as varchar), '') || '-' || coalesce(cast(conflict_stream_name as varchar), '')

 as varchar)) as _airbyte_conflict_stream_array_2_hashid
from __dbt__CTE__conflict_stream_array_conflict_stream_array_ab2
-- conflict_stream_array at conflict_stream_array/conflict_stream_array
)-- Final base SQL model
select
    _airbyte_conflict_stream_array_hashid,
    conflict_stream_name,
    _airbyte_emitted_at,
    _airbyte_conflict_stream_array_2_hashid
from __dbt__CTE__conflict_stream_array_conflict_stream_array_ab3
-- conflict_stream_array at conflict_stream_array/conflict_stream_array from "integrationtests".test_normalization."conflict_stream_array"
  );