

  create  table
    "integrationtests".test_normalization."unnest_alias__dbt_tmp"
    
    
  as (
    
with __dbt__CTE__unnest_alias_ab1 as (

-- SQL model to parse JSON blob stored in a single column and extract into separated field columns as described by the JSON Schema
select
    case when json_extract_path_text(_airbyte_data, 'id', true) != '' then json_extract_path_text(_airbyte_data, 'id', true) end as id,
    json_extract_path_text(_airbyte_data, 'children', true) as children,
    _airbyte_emitted_at
from "integrationtests".test_normalization._airbyte_raw_unnest_alias as table_alias
-- unnest_alias
),  __dbt__CTE__unnest_alias_ab2 as (

-- SQL model to cast each column to its adequate SQL type converted from the JSON schema type
select
    cast(id as 
    bigint
) as id,
    children,
    _airbyte_emitted_at
from __dbt__CTE__unnest_alias_ab1
-- unnest_alias
),  __dbt__CTE__unnest_alias_ab3 as (

-- SQL model to build a hash column based on the values of this record
select
    *,
    md5(cast(
    
    coalesce(cast(id as varchar), '') || '-' || coalesce(cast(children as varchar), '')

 as varchar)) as _airbyte_unnest_alias_hashid
from __dbt__CTE__unnest_alias_ab2
-- unnest_alias
)-- Final base SQL model
select
    id,
    children,
    _airbyte_emitted_at,
    _airbyte_unnest_alias_hashid
from __dbt__CTE__unnest_alias_ab3
-- unnest_alias from "integrationtests".test_normalization._airbyte_raw_unnest_alias
  );