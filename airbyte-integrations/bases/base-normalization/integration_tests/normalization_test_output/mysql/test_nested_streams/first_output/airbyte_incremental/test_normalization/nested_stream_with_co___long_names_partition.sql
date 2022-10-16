

  create  table
    test_normalization.`nested_stream_with_co___long_names_partition__dbt_tmp`
  as (
    
with __dbt__cte__nested_stream_with_co_2g_names_partition_ab1 as (

-- SQL model to parse JSON blob stored in a single column and extract into separated field columns as described by the JSON Schema
-- depends_on: test_normalization.`nested_stream_with_co_1g_into_long_names_scd`
select
    _airbyte_nested_strea__nto_long_names_hashid,
    json_extract(`partition`, 
    '$."double_array_data"') as double_array_data,
    json_extract(`partition`, 
    '$."DATA"') as `DATA`,
    _airbyte_ab_id,
    _airbyte_emitted_at,
    
    CURRENT_TIMESTAMP
 as _airbyte_normalized_at
from test_normalization.`nested_stream_with_co_1g_into_long_names_scd` as table_alias
-- partition at nested_stream_with_complex_columns_resulting_into_long_names/partition
where 1 = 1
and `partition` is not null

),  __dbt__cte__nested_stream_with_co_2g_names_partition_ab2 as (

-- SQL model to cast each column to its adequate SQL type converted from the JSON schema type
-- depends_on: __dbt__cte__nested_stream_with_co_2g_names_partition_ab1
select
    _airbyte_nested_strea__nto_long_names_hashid,
    double_array_data,
    `DATA`,
    _airbyte_ab_id,
    _airbyte_emitted_at,
    
    CURRENT_TIMESTAMP
 as _airbyte_normalized_at
from __dbt__cte__nested_stream_with_co_2g_names_partition_ab1
-- partition at nested_stream_with_complex_columns_resulting_into_long_names/partition
where 1 = 1

),  __dbt__cte__nested_stream_with_co_2g_names_partition_ab3 as (

-- SQL model to build a hash column based on the values of this record
-- depends_on: __dbt__cte__nested_stream_with_co_2g_names_partition_ab2
select
    md5(cast(concat(coalesce(cast(_airbyte_nested_strea__nto_long_names_hashid as char), ''), '-', coalesce(cast(double_array_data as char), ''), '-', coalesce(cast(`DATA` as char), '')) as char)) as _airbyte_partition_hashid,
    tmp.*
from __dbt__cte__nested_stream_with_co_2g_names_partition_ab2 tmp
-- partition at nested_stream_with_complex_columns_resulting_into_long_names/partition
where 1 = 1

)-- Final base SQL model
-- depends_on: __dbt__cte__nested_stream_with_co_2g_names_partition_ab3
select
    _airbyte_nested_strea__nto_long_names_hashid,
    double_array_data,
    `DATA`,
    _airbyte_ab_id,
    _airbyte_emitted_at,
    
    CURRENT_TIMESTAMP
 as _airbyte_normalized_at,
    _airbyte_partition_hashid
from __dbt__cte__nested_stream_with_co_2g_names_partition_ab3
-- partition at nested_stream_with_complex_columns_resulting_into_long_names/partition from test_normalization.`nested_stream_with_co_1g_into_long_names_scd`
where 1 = 1

  )
