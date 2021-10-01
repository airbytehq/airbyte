

  create or replace table `dataline-integration-testing`.test_normalization_namespace.`simple_stream_with_namespace_resulting_into_long_names`
  
  
  OPTIONS()
  as (
    
with __dbt__CTE__simple_stream_with_namespace_resulting_into_long_names_ab1 as (

-- SQL model to parse JSON blob stored in a single column and extract into separated field columns as described by the JSON Schema
select
    json_extract_scalar(_airbyte_data, "$['id']") as id,
    json_extract_scalar(_airbyte_data, "$['date']") as date,
    _airbyte_emitted_at
from `dataline-integration-testing`.test_normalization_namespace._airbyte_raw_simple_stream_with_namespace_resulting_into_long_names as table_alias
-- simple_stream_with_namespace_resulting_into_long_names
),  __dbt__CTE__simple_stream_with_namespace_resulting_into_long_names_ab2 as (

-- SQL model to cast each column to its adequate SQL type converted from the JSON schema type
select
    cast(id as 
    string
) as id,
    cast(date as 
    string
) as date,
    _airbyte_emitted_at
from __dbt__CTE__simple_stream_with_namespace_resulting_into_long_names_ab1
-- simple_stream_with_namespace_resulting_into_long_names
),  __dbt__CTE__simple_stream_with_namespace_resulting_into_long_names_ab3 as (

-- SQL model to build a hash column based on the values of this record
select
    to_hex(md5(cast(concat(coalesce(cast(id as 
    string
), ''), '-', coalesce(cast(date as 
    string
), '')) as 
    string
))) as _airbyte_simple_stream_with_namespace_resulting_into_long_names_hashid,
    tmp.*
from __dbt__CTE__simple_stream_with_namespace_resulting_into_long_names_ab2 tmp
-- simple_stream_with_namespace_resulting_into_long_names
)-- Final base SQL model
select
    id,
    date,
    _airbyte_emitted_at,
    _airbyte_simple_stream_with_namespace_resulting_into_long_names_hashid
from __dbt__CTE__simple_stream_with_namespace_resulting_into_long_names_ab3
-- simple_stream_with_namespace_resulting_into_long_names from `dataline-integration-testing`.test_normalization_namespace._airbyte_raw_simple_stream_with_namespace_resulting_into_long_names
  );
    