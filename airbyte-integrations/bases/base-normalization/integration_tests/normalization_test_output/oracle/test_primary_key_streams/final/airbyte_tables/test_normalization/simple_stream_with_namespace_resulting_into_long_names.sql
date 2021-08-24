

  create  table test_normalization.simple_stream_with_namespace_resulting_into_long_names__dbt_tmp
  
  as
    
with dbt__cte__simple_stream_with_namespace_resulting_into_long_names_ab1__ as (

-- SQL model to parse JSON blob stored in a single column and extract into separated field columns as described by the JSON Schema
select
    json_value(airbyte_data, '$."id"') as id,
    json_value(airbyte_data, '$."date"') as "DATE",
    airbyte_emitted_at
from test_normalization.airbyte_raw_simple_stream_with_namespace_resulting_into_long_names 
-- simple_stream_with_namespace_resulting_into_long_names
),  dbt__cte__simple_stream_with_namespace_resulting_into_long_names_ab2__ as (

-- SQL model to cast each column to its adequate SQL type converted from the JSON schema type
select
    cast(id as varchar2(4000)) as id,
    cast("DATE" as varchar2(4000)) as "DATE",
    airbyte_emitted_at
from dbt__cte__simple_stream_with_namespace_resulting_into_long_names_ab1__
-- simple_stream_with_namespace_resulting_into_long_names
),  dbt__cte__simple_stream_with_namespace_resulting_into_long_names_ab3__ as (

-- SQL model to build a hash column based on the values of this record
select
    ora_hash(
        'id' || '~' ||
        "DATE"
    ) as "_AIRBYTE_SIMPLE_STREAM_WITH_NAMESPACE_RESULTING_INTO_LONG_NAMES_HASHID",
    tmp.*
from dbt__cte__simple_stream_with_namespace_resulting_into_long_names_ab2__ tmp
-- simple_stream_with_namespace_resulting_into_long_names
)-- Final base SQL model
select
    id,
    "DATE",
    airbyte_emitted_at,
    "_AIRBYTE_SIMPLE_STREAM_WITH_NAMESPACE_RESULTING_INTO_LONG_NAMES_HASHID"
from dbt__cte__simple_stream_with_namespace_resulting_into_long_names_ab3__
-- simple_stream_with_namespace_resulting_into_long_names from test_normalization.airbyte_raw_simple_stream_with_namespace_resulting_into_long_names