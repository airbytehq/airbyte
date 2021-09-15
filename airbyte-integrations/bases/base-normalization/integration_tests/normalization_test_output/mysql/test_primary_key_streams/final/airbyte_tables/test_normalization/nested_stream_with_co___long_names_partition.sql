

  create  table
    test_normalization.`nested_stream_with_co___long_names_partition__dbt_tmp`
  as (
    
with __dbt__CTE__nested_stream_with_co_2g_names_partition_ab1 as (

-- SQL model to parse JSON blob stored in a single column and extract into separated field columns as described by the JSON Schema
select
    _airbyte_nested_strea__nto_long_names_hashid,
    json_extract(`partition`, 
    '$."double_array_data"') as double_array_data,
    json_extract(`partition`, 
    '$."DATA"') as `DATA`,
    json_extract(`partition`, 
    '$."column___with__quotes"') as `column__'with"_quotes`,
    _airbyte_emitted_at
from test_normalization.`nested_stream_with_co__lting_into_long_names` as table_alias
where `partition` is not null
-- partition at nested_stream_with_complex_columns_resulting_into_long_names/partition
),  __dbt__CTE__nested_stream_with_co_2g_names_partition_ab2 as (

-- SQL model to cast each column to its adequate SQL type converted from the JSON schema type
select
    _airbyte_nested_strea__nto_long_names_hashid,
    double_array_data,
    `DATA`,
    `column__'with"_quotes`,
    _airbyte_emitted_at
from __dbt__CTE__nested_stream_with_co_2g_names_partition_ab1
-- partition at nested_stream_with_complex_columns_resulting_into_long_names/partition
),  __dbt__CTE__nested_stream_with_co_2g_names_partition_ab3 as (

-- SQL model to build a hash column based on the values of this record
select
    md5(cast(concat(coalesce(cast(_airbyte_nested_strea__nto_long_names_hashid as char), ''), '-', coalesce(cast(double_array_data as char), ''), '-', coalesce(cast(`DATA` as char), ''), '-', coalesce(cast(`column__'with"_quotes` as char), '')) as char)) as _airbyte_partition_hashid,
    tmp.*
from __dbt__CTE__nested_stream_with_co_2g_names_partition_ab2 tmp
-- partition at nested_stream_with_complex_columns_resulting_into_long_names/partition
)-- Final base SQL model
select
    _airbyte_nested_strea__nto_long_names_hashid,
    double_array_data,
    `DATA`,
    `column__'with"_quotes`,
    _airbyte_emitted_at,
    _airbyte_partition_hashid
from __dbt__CTE__nested_stream_with_co_2g_names_partition_ab3
-- partition at nested_stream_with_complex_columns_resulting_into_long_names/partition from test_normalization.`nested_stream_with_co__lting_into_long_names`
  )
