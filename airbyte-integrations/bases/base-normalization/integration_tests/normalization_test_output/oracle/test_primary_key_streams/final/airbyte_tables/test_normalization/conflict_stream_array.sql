

  create  table test_normalization.conflict_stream_array__dbt_tmp
  
  as
    
with dbt__cte__conflict_stream_array_ab1__ as (

-- SQL model to parse JSON blob stored in a single column and extract into separated field columns as described by the JSON Schema
select
    json_value("_AIRBYTE_DATA", '$."id"') as id,
    json_value("_AIRBYTE_DATA", '$."conflict_stream_array"') as conflict_stream_array,
    "_AIRBYTE_EMITTED_AT"
from test_normalization.airbyte_raw_conflict_stream_array 
-- conflict_stream_array
),  dbt__cte__conflict_stream_array_ab2__ as (

-- SQL model to cast each column to its adequate SQL type converted from the JSON schema type
select
    cast(id as varchar2(4000)) as id,
    conflict_stream_array,
    "_AIRBYTE_EMITTED_AT"
from dbt__cte__conflict_stream_array_ab1__
-- conflict_stream_array
),  dbt__cte__conflict_stream_array_ab3__ as (

-- SQL model to build a hash column based on the values of this record
select
    ora_hash(
            
                id || '~' ||
            
            
                cast(conflict_stream_array as varchar2(4000))
            
    ) as "_AIRBYTE_CONFLICT_STREAM_ARRAY_HASHID",
    tmp.*
from dbt__cte__conflict_stream_array_ab2__ tmp
-- conflict_stream_array
)-- Final base SQL model
select
    id,
    conflict_stream_array,
    "_AIRBYTE_EMITTED_AT",
    "_AIRBYTE_CONFLICT_STREAM_ARRAY_HASHID"
from dbt__cte__conflict_stream_array_ab3__
-- conflict_stream_array from test_normalization.airbyte_raw_conflict_stream_array