

  create  table test_normalization.conflict_stream_scalar__dbt_tmp
  
  as
    
with dbt__cte__conflict_stream_scalar_ab1__ as (

-- SQL model to parse JSON blob stored in a single column and extract into separated field columns as described by the JSON Schema
select
    json_value("_AIRBYTE_DATA", '$."id"') as id,
    json_value("_AIRBYTE_DATA", '$."conflict_stream_scalar"') as conflict_stream_scalar,
    "_AIRBYTE_EMITTED_AT"
from test_normalization.airbyte_raw_conflict_stream_scalar 
-- conflict_stream_scalar
),  dbt__cte__conflict_stream_scalar_ab2__ as (

-- SQL model to cast each column to its adequate SQL type converted from the JSON schema type
select
    cast(id as varchar2(4000)) as id,
    cast(conflict_stream_scalar as 
    numeric
) as conflict_stream_scalar,
    "_AIRBYTE_EMITTED_AT"
from dbt__cte__conflict_stream_scalar_ab1__
-- conflict_stream_scalar
),  dbt__cte__conflict_stream_scalar_ab3__ as (

-- SQL model to build a hash column based on the values of this record
select
    ora_hash(
            
                id || '~' ||
            
            
                conflict_stream_scalar
            
    ) as "_AIRBYTE_CONFLICT_STREAM_SCALAR_HASHID",
    tmp.*
from dbt__cte__conflict_stream_scalar_ab2__ tmp
-- conflict_stream_scalar
)-- Final base SQL model
select
    id,
    conflict_stream_scalar,
    "_AIRBYTE_EMITTED_AT",
    "_AIRBYTE_CONFLICT_STREAM_SCALAR_HASHID"
from dbt__cte__conflict_stream_scalar_ab3__
-- conflict_stream_scalar from test_normalization.airbyte_raw_conflict_stream_scalar