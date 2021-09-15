

      create or replace transient table "AIRBYTE_DATABASE".TEST_NORMALIZATION."CONFLICT_STREAM_NAME_CONFLICT_STREAM_NAME_CONFLICT_STREAM_NAME"  as
      (
with __dbt__CTE__CONFLICT_STREAM_NAME_CONFLICT_STREAM_NAME_CONFLICT_STREAM_NAME_AB1 as (

-- SQL model to parse JSON blob stored in a single column and extract into separated field columns as described by the JSON Schema
select
    _AIRBYTE_CONFLICT_STREAM_NAME_2_HASHID,
    to_varchar(get_path(parse_json(CONFLICT_STREAM_NAME), '"groups"')) as GROUPS,
    _AIRBYTE_EMITTED_AT
from "AIRBYTE_DATABASE".TEST_NORMALIZATION."CONFLICT_STREAM_NAME_CONFLICT_STREAM_NAME" as table_alias
where CONFLICT_STREAM_NAME is not null
-- CONFLICT_STREAM_NAME at conflict_stream_name/conflict_stream_name/conflict_stream_name
),  __dbt__CTE__CONFLICT_STREAM_NAME_CONFLICT_STREAM_NAME_CONFLICT_STREAM_NAME_AB2 as (

-- SQL model to cast each column to its adequate SQL type converted from the JSON schema type
select
    _AIRBYTE_CONFLICT_STREAM_NAME_2_HASHID,
    cast(GROUPS as 
    varchar
) as GROUPS,
    _AIRBYTE_EMITTED_AT
from __dbt__CTE__CONFLICT_STREAM_NAME_CONFLICT_STREAM_NAME_CONFLICT_STREAM_NAME_AB1
-- CONFLICT_STREAM_NAME at conflict_stream_name/conflict_stream_name/conflict_stream_name
),  __dbt__CTE__CONFLICT_STREAM_NAME_CONFLICT_STREAM_NAME_CONFLICT_STREAM_NAME_AB3 as (

-- SQL model to build a hash column based on the values of this record
select
    md5(cast(
    
    coalesce(cast(_AIRBYTE_CONFLICT_STREAM_NAME_2_HASHID as 
    varchar
), '') || '-' || coalesce(cast(GROUPS as 
    varchar
), '')

 as 
    varchar
)) as _AIRBYTE_CONFLICT_STREAM_NAME_3_HASHID,
    tmp.*
from __dbt__CTE__CONFLICT_STREAM_NAME_CONFLICT_STREAM_NAME_CONFLICT_STREAM_NAME_AB2 tmp
-- CONFLICT_STREAM_NAME at conflict_stream_name/conflict_stream_name/conflict_stream_name
)-- Final base SQL model
select
    _AIRBYTE_CONFLICT_STREAM_NAME_2_HASHID,
    GROUPS,
    _AIRBYTE_EMITTED_AT,
    _AIRBYTE_CONFLICT_STREAM_NAME_3_HASHID
from __dbt__CTE__CONFLICT_STREAM_NAME_CONFLICT_STREAM_NAME_CONFLICT_STREAM_NAME_AB3
-- CONFLICT_STREAM_NAME at conflict_stream_name/conflict_stream_name/conflict_stream_name from "AIRBYTE_DATABASE".TEST_NORMALIZATION."CONFLICT_STREAM_NAME_CONFLICT_STREAM_NAME"
      );
    