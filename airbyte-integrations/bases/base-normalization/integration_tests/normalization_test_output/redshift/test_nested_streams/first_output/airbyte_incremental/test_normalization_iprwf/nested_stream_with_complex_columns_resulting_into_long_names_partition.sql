
      

  create  table
    "normalization_tests".test_normalization_iprwf."nested_stream_with_complex_columns_resulting_into_long_names_partition"
    
    
      compound sortkey(_airbyte_emitted_at)
    
  as (
    
with __dbt__cte__nested_stream_with_complex_columns_resulting_into_long_names_partition_ab1 as (

-- SQL model to parse JSON blob stored in a single column and extract into separated field columns as described by the JSON Schema
-- depends_on: "normalization_tests".test_normalization_iprwf."nested_stream_with_complex_columns_resulting_into_long_names_scd"
select
    _airbyte_nested_stream_with_complex_columns_resulting_into_long_names_hashid,
    "partition"."double_array_data" as double_array_data,
    "partition"."DATA" as data,
    _airbyte_ab_id,
    _airbyte_emitted_at,
    getdate() as _airbyte_normalized_at
from "normalization_tests".test_normalization_iprwf."nested_stream_with_complex_columns_resulting_into_long_names_scd" as table_alias
-- partition at nested_stream_with_complex_columns_resulting_into_long_names/partition
where 1 = 1
and "partition" is not null

),  __dbt__cte__nested_stream_with_complex_columns_resulting_into_long_names_partition_ab2 as (

-- SQL model to cast each column to its adequate SQL type converted from the JSON schema type
-- depends_on: __dbt__cte__nested_stream_with_complex_columns_resulting_into_long_names_partition_ab1
select
    _airbyte_nested_stream_with_complex_columns_resulting_into_long_names_hashid,
    double_array_data,
    data,
    _airbyte_ab_id,
    _airbyte_emitted_at,
    getdate() as _airbyte_normalized_at
from __dbt__cte__nested_stream_with_complex_columns_resulting_into_long_names_partition_ab1
-- partition at nested_stream_with_complex_columns_resulting_into_long_names/partition
where 1 = 1

),  __dbt__cte__nested_stream_with_complex_columns_resulting_into_long_names_partition_ab3 as (

-- SQL model to build a hash column based on the values of this record
-- depends_on: __dbt__cte__nested_stream_with_complex_columns_resulting_into_long_names_partition_ab2
select
    md5(cast(coalesce(cast(_airbyte_nested_stream_with_complex_columns_resulting_into_long_names_hashid as text), '') || '-' || coalesce(cast(json_serialize(double_array_data) as text), '') || '-' || coalesce(cast(json_serialize(data) as text), '') as text)) as _airbyte_partition_hashid,
    tmp.*
from __dbt__cte__nested_stream_with_complex_columns_resulting_into_long_names_partition_ab2 tmp
-- partition at nested_stream_with_complex_columns_resulting_into_long_names/partition
where 1 = 1

)-- Final base SQL model
-- depends_on: __dbt__cte__nested_stream_with_complex_columns_resulting_into_long_names_partition_ab3
select
    _airbyte_nested_stream_with_complex_columns_resulting_into_long_names_hashid,
    double_array_data,
    data,
    _airbyte_ab_id,
    _airbyte_emitted_at,
    getdate() as _airbyte_normalized_at,
    _airbyte_partition_hashid
from __dbt__cte__nested_stream_with_complex_columns_resulting_into_long_names_partition_ab3
-- partition at nested_stream_with_complex_columns_resulting_into_long_names/partition from "normalization_tests".test_normalization_iprwf."nested_stream_with_complex_columns_resulting_into_long_names_scd"
where 1 = 1

  );
  