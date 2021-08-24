

  create  table test_normalization.conflict_stream_name__dbt_tmp
  
  as
    
with dbt__cte__conflict_stream_name_ab1__ as (

-- SQL model to parse JSON blob stored in a single column and extract into separated field columns as described by the JSON Schema
select
    json_value(airbyte_data, '$."id"') as id,
    
        json_value(airbyte_data, '$."conflict_stream_name"')
     as conflict_stream_name,
    airbyte_emitted_at
from test_normalization.airbyte_raw_conflict_stream_name 
-- conflict_stream_name
),  dbt__cte__conflict_stream_name_ab2__ as (

-- SQL model to cast each column to its adequate SQL type converted from the JSON schema type
select
    cast(id as varchar2(4000)) as id,
    cast(conflict_stream_name as varchar2(4000)) as conflict_stream_name,
    airbyte_emitted_at
from dbt__cte__conflict_stream_name_ab1__
-- conflict_stream_name
),  dbt__cte__conflict_stream_name_ab3__ as (

-- SQL model to build a hash column based on the values of this record
select
    ora_hash(
        'id' || '~' ||
        'conflict_stream_name'
    ) as "_AIRBYTE_CONFLICT_STREAM_NAME_HASHID",
    tmp.*
from dbt__cte__conflict_stream_name_ab2__ tmp
-- conflict_stream_name
)-- Final base SQL model
select
    id,
    conflict_stream_name,
    airbyte_emitted_at,
    "_AIRBYTE_CONFLICT_STREAM_NAME_HASHID"
from dbt__cte__conflict_stream_name_ab3__
-- conflict_stream_name from test_normalization.airbyte_raw_conflict_stream_name