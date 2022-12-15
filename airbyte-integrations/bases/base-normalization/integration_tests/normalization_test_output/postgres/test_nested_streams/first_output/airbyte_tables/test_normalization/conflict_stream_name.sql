

  create  table "postgres".test_normalization."conflict_stream_name__dbt_tmp"
  as (
    
with __dbt__cte__conflict_stream_name_ab1 as (

-- SQL model to parse JSON blob stored in a single column and extract into separated field columns as described by the JSON Schema
-- depends_on: "postgres".test_normalization._airbyte_raw_conflict_stream_name
select
    jsonb_extract_path_text(_airbyte_data, 'id') as "id",
    
        jsonb_extract_path(table_alias._airbyte_data, 'conflict_stream_name')
     as conflict_stream_name,
    _airbyte_ab_id,
    _airbyte_emitted_at,
    now() as _airbyte_normalized_at
from "postgres".test_normalization._airbyte_raw_conflict_stream_name as table_alias
-- conflict_stream_name
where 1 = 1
),  __dbt__cte__conflict_stream_name_ab2 as (

-- SQL model to cast each column to its adequate SQL type converted from the JSON schema type
-- depends_on: __dbt__cte__conflict_stream_name_ab1
select
    cast("id" as text) as "id",
    cast(conflict_stream_name as 
    jsonb
) as conflict_stream_name,
    _airbyte_ab_id,
    _airbyte_emitted_at,
    now() as _airbyte_normalized_at
from __dbt__cte__conflict_stream_name_ab1
-- conflict_stream_name
where 1 = 1
),  __dbt__cte__conflict_stream_name_ab3 as (

-- SQL model to build a hash column based on the values of this record
-- depends_on: __dbt__cte__conflict_stream_name_ab2
select
    md5(cast(coalesce(cast("id" as text), '') || '-' || coalesce(cast(conflict_stream_name as text), '') as text)) as _airbyte_conflict_stream_name_hashid,
    tmp.*
from __dbt__cte__conflict_stream_name_ab2 tmp
-- conflict_stream_name
where 1 = 1
)-- Final base SQL model
-- depends_on: __dbt__cte__conflict_stream_name_ab3
select
    "id",
    conflict_stream_name,
    _airbyte_ab_id,
    _airbyte_emitted_at,
    now() as _airbyte_normalized_at,
    _airbyte_conflict_stream_name_hashid
from __dbt__cte__conflict_stream_name_ab3
-- conflict_stream_name from "postgres".test_normalization._airbyte_raw_conflict_stream_name
where 1 = 1
  );