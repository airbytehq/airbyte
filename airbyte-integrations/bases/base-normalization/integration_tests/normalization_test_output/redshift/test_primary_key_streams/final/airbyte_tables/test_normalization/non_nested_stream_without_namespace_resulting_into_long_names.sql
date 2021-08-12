

  create  table
    "integrationtests".test_normalization."non_nested_stream_without_namespace_resulting_into_long_names__dbt_tmp"
    
    
  as (
    
with __dbt__CTE__non_nested_stream_without_namespace_resulting_into_long_names_ab1 as (

-- SQL model to parse JSON blob stored in a single column and extract into separated field columns as described by the JSON Schema
select
    case when json_extract_path_text(_airbyte_data, 'id', true) != '' then json_extract_path_text(_airbyte_data, 'id', true) end as id,
    case when json_extract_path_text(_airbyte_data, 'date', true) != '' then json_extract_path_text(_airbyte_data, 'date', true) end as date,
    _airbyte_emitted_at
from "integrationtests".test_normalization._airbyte_raw_non_nested_stream_without_namespace_resulting_into_long_names as table_alias
-- non_nested_stream_without_namespace_resulting_into_long_names
),  __dbt__CTE__non_nested_stream_without_namespace_resulting_into_long_names_ab2 as (

-- SQL model to cast each column to its adequate SQL type converted from the JSON schema type
select
    cast(id as varchar) as id,
    cast(date as varchar) as date,
    _airbyte_emitted_at
from __dbt__CTE__non_nested_stream_without_namespace_resulting_into_long_names_ab1
-- non_nested_stream_without_namespace_resulting_into_long_names
),  __dbt__CTE__non_nested_stream_without_namespace_resulting_into_long_names_ab3 as (

-- SQL model to build a hash column based on the values of this record
select
    *,
    md5(cast(
    
    coalesce(cast(id as varchar), '') || '-' || coalesce(cast(date as varchar), '')

 as varchar)) as _airbyte_non_nested_stream_without_namespace_resulting_into_long_names_hashid
from __dbt__CTE__non_nested_stream_without_namespace_resulting_into_long_names_ab2
-- non_nested_stream_without_namespace_resulting_into_long_names
)-- Final base SQL model
select
    id,
    date,
    _airbyte_emitted_at,
    _airbyte_non_nested_stream_without_namespace_resulting_into_long_names_hashid
from __dbt__CTE__non_nested_stream_without_namespace_resulting_into_long_names_ab3
-- non_nested_stream_without_namespace_resulting_into_long_names from "integrationtests".test_normalization._airbyte_raw_non_nested_stream_without_namespace_resulting_into_long_names
  );