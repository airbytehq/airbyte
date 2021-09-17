

  create  table test_normalization.conflict_stream_name_conflict_stream_name_conflict_stream_name__dbt_tmp
  
  as
    
with dbt__cte__conflict_stream_name_conflict_stream_name_conflict_stream_name_ab1__ as (

-- SQL model to parse JSON blob stored in a single column and extract into separated field columns as described by the JSON Schema
select
    "_AIRBYTE_CONFLICT_STREAM_NAME_2_HASHID",
    json_value(conflict_stream_name, '$."groups"') as groups,
    "_AIRBYTE_EMITTED_AT"
from test_normalization.conflict_stream_name_conflict_stream_name 
where conflict_stream_name is not null
-- conflict_stream_name at conflict_stream_name/conflict_stream_name/conflict_stream_name
),  dbt__cte__conflict_stream_name_conflict_stream_name_conflict_stream_name_ab2__ as (

-- SQL model to cast each column to its adequate SQL type converted from the JSON schema type
select
    "_AIRBYTE_CONFLICT_STREAM_NAME_2_HASHID",
    cast(groups as varchar2(4000)) as groups,
    "_AIRBYTE_EMITTED_AT"
from dbt__cte__conflict_stream_name_conflict_stream_name_conflict_stream_name_ab1__
-- conflict_stream_name at conflict_stream_name/conflict_stream_name/conflict_stream_name
),  dbt__cte__conflict_stream_name_conflict_stream_name_conflict_stream_name_ab3__ as (

-- SQL model to build a hash column based on the values of this record
select
    ora_hash(
            
                "_AIRBYTE_CONFLICT_STREAM_NAME_2_HASHID" || '~' ||
            
            
                groups
            
    ) as "_AIRBYTE_CONFLICT_STREAM_NAME_3_HASHID",
    tmp.*
from dbt__cte__conflict_stream_name_conflict_stream_name_conflict_stream_name_ab2__ tmp
-- conflict_stream_name at conflict_stream_name/conflict_stream_name/conflict_stream_name
)-- Final base SQL model
select
    "_AIRBYTE_CONFLICT_STREAM_NAME_2_HASHID",
    groups,
    "_AIRBYTE_EMITTED_AT",
    "_AIRBYTE_CONFLICT_STREAM_NAME_3_HASHID"
from dbt__cte__conflict_stream_name_conflict_stream_name_conflict_stream_name_ab3__
-- conflict_stream_name at conflict_stream_name/conflict_stream_name/conflict_stream_name from test_normalization.conflict_stream_name_conflict_stream_name