

  create  table test_normalization.non_nested_stream_without_namespace_resulting_into_long_names__dbt_tmp
  
  as
    
with dbt__cte__non_nested_stream_without_namespace_resulting_into_long_names_ab1__ as (

-- SQL model to parse JSON blob stored in a single column and extract into separated field columns as described by the JSON Schema
select
    json_value("_AIRBYTE_DATA", '$."id"') as id,
    json_value("_AIRBYTE_DATA", '$."date"') as "DATE",
    "_AIRBYTE_EMITTED_AT"
from test_normalization.airbyte_raw_non_nested_stream_without_namespace_resulting_into_long_names 
-- non_nested_stream_without_namespace_resulting_into_long_names
),  dbt__cte__non_nested_stream_without_namespace_resulting_into_long_names_ab2__ as (

-- SQL model to cast each column to its adequate SQL type converted from the JSON schema type
select
    cast(id as varchar2(4000)) as id,
    cast("DATE" as varchar2(4000)) as "DATE",
    "_AIRBYTE_EMITTED_AT"
from dbt__cte__non_nested_stream_without_namespace_resulting_into_long_names_ab1__
-- non_nested_stream_without_namespace_resulting_into_long_names
),  dbt__cte__non_nested_stream_without_namespace_resulting_into_long_names_ab3__ as (

-- SQL model to build a hash column based on the values of this record
select
    ora_hash(
            
                id || '~' ||
            
            
                "DATE"
            
    ) as "_AIRBYTE_NON_NESTED_STREAM_WITHOUT_NAMESPACE_RESULTING_INTO_LONG_NAMES_HASHID",
    tmp.*
from dbt__cte__non_nested_stream_without_namespace_resulting_into_long_names_ab2__ tmp
-- non_nested_stream_without_namespace_resulting_into_long_names
)-- Final base SQL model
select
    id,
    "DATE",
    "_AIRBYTE_EMITTED_AT",
    "_AIRBYTE_NON_NESTED_STREAM_WITHOUT_NAMESPACE_RESULTING_INTO_LONG_NAMES_HASHID"
from dbt__cte__non_nested_stream_without_namespace_resulting_into_long_names_ab3__
-- non_nested_stream_without_namespace_resulting_into_long_names from test_normalization.airbyte_raw_non_nested_stream_without_namespace_resulting_into_long_names