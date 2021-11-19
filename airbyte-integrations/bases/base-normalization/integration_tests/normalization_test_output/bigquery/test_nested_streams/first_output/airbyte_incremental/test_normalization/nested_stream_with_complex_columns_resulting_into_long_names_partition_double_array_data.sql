

  create or replace table `dataline-integration-testing`.test_normalization.`nested_stream_with_complex_columns_resulting_into_long_names_partition_double_array_data`
  partition by timestamp_trunc(_airbyte_emitted_at, day)
  cluster by _airbyte_emitted_at
  OPTIONS()
  as (
    
with __dbt__cte__nested_stream_with_complex_columns_resulting_into_long_names_partition_double_array_data_ab1 as (

-- SQL model to parse JSON blob stored in a single column and extract into separated field columns as described by the JSON Schema
-- depends_on: `dataline-integration-testing`.test_normalization.`nested_stream_with_complex_columns_resulting_into_long_names_partition`

select
    _airbyte_partition_hashid,
    json_extract_scalar(double_array_data, "$['id']") as id,
    _airbyte_ab_id,
    _airbyte_emitted_at,
    CURRENT_TIMESTAMP() as _airbyte_normalized_at
from `dataline-integration-testing`.test_normalization.`nested_stream_with_complex_columns_resulting_into_long_names_partition` as table_alias
-- double_array_data at nested_stream_with_complex_columns_resulting_into_long_names/partition/double_array_data
cross join unnest(double_array_data) as double_array_data
where 1 = 1
and double_array_data is not null

),  __dbt__cte__nested_stream_with_complex_columns_resulting_into_long_names_partition_double_array_data_ab2 as (

-- SQL model to cast each column to its adequate SQL type converted from the JSON schema type
-- depends_on: __dbt__cte__nested_stream_with_complex_columns_resulting_into_long_names_partition_double_array_data_ab1
select
    _airbyte_partition_hashid,
    cast(id as 
    string
) as id,
    _airbyte_ab_id,
    _airbyte_emitted_at,
    CURRENT_TIMESTAMP() as _airbyte_normalized_at
from __dbt__cte__nested_stream_with_complex_columns_resulting_into_long_names_partition_double_array_data_ab1
-- double_array_data at nested_stream_with_complex_columns_resulting_into_long_names/partition/double_array_data
where 1 = 1

),  __dbt__cte__nested_stream_with_complex_columns_resulting_into_long_names_partition_double_array_data_ab3 as (

-- SQL model to build a hash column based on the values of this record
-- depends_on: __dbt__cte__nested_stream_with_complex_columns_resulting_into_long_names_partition_double_array_data_ab2
select
    to_hex(md5(cast(concat(coalesce(cast(_airbyte_partition_hashid as 
    string
), ''), '-', coalesce(cast(id as 
    string
), '')) as 
    string
))) as _airbyte_double_array_data_hashid,
    tmp.*
from __dbt__cte__nested_stream_with_complex_columns_resulting_into_long_names_partition_double_array_data_ab2 tmp
-- double_array_data at nested_stream_with_complex_columns_resulting_into_long_names/partition/double_array_data
where 1 = 1

)-- Final base SQL model
-- depends_on: __dbt__cte__nested_stream_with_complex_columns_resulting_into_long_names_partition_double_array_data_ab3
select
    _airbyte_partition_hashid,
    id,
    _airbyte_ab_id,
    _airbyte_emitted_at,
    CURRENT_TIMESTAMP() as _airbyte_normalized_at,
    _airbyte_double_array_data_hashid
from __dbt__cte__nested_stream_with_complex_columns_resulting_into_long_names_partition_double_array_data_ab3
-- double_array_data at nested_stream_with_complex_columns_resulting_into_long_names/partition/double_array_data from `dataline-integration-testing`.test_normalization.`nested_stream_with_complex_columns_resulting_into_long_names_partition`
where 1 = 1

  );
  