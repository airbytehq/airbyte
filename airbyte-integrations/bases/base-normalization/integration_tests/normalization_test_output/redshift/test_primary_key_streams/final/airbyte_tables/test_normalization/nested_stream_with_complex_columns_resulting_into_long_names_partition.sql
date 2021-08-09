

  create  table
    "integrationtests".test_normalization."nested_stream_with_complex_columns_resulting_into_long_names_partition__dbt_tmp"
    
    
  as (
    
with __dbt__CTE__nested_stream_with_complex_columns_resulting_into_long_names_partition_ab1 as (

-- SQL model to parse JSON blob stored in a single column and extract into separated field columns as described by the JSON Schema
select
    _airbyte_nested_stream_with_complex_columns_resulting_into_long_names_hashid,
    json_extract_path_text("partition", 'double_array_data', true) as double_array_data,
    json_extract_path_text("partition", 'DATA', true) as data,
    json_extract_path_text("partition", 'column`_''with"_quotes', true) as "column`_'with""_quotes",
    _airbyte_emitted_at
from "integrationtests".test_normalization."nested_stream_with_complex_columns_resulting_into_long_names" as table_alias
where "partition" is not null
-- partition at nested_stream_with_complex_columns_resulting_into_long_names/partition
),  __dbt__CTE__nested_stream_with_complex_columns_resulting_into_long_names_partition_ab2 as (

-- SQL model to cast each column to its adequate SQL type converted from the JSON schema type
select
    _airbyte_nested_stream_with_complex_columns_resulting_into_long_names_hashid,
    double_array_data,
    data,
    "column`_'with""_quotes",
    _airbyte_emitted_at
from __dbt__CTE__nested_stream_with_complex_columns_resulting_into_long_names_partition_ab1
-- partition at nested_stream_with_complex_columns_resulting_into_long_names/partition
),  __dbt__CTE__nested_stream_with_complex_columns_resulting_into_long_names_partition_ab3 as (

-- SQL model to build a hash column based on the values of this record
select
    *,
    md5(cast(
    
    coalesce(cast(_airbyte_nested_stream_with_complex_columns_resulting_into_long_names_hashid as varchar), '') || '-' || coalesce(cast(double_array_data as varchar), '') || '-' || coalesce(cast(data as varchar), '') || '-' || coalesce(cast("column`_'with""_quotes" as varchar), '')

 as varchar)) as _airbyte_partition_hashid
from __dbt__CTE__nested_stream_with_complex_columns_resulting_into_long_names_partition_ab2
-- partition at nested_stream_with_complex_columns_resulting_into_long_names/partition
)-- Final base SQL model
select
    _airbyte_nested_stream_with_complex_columns_resulting_into_long_names_hashid,
    double_array_data,
    data,
    "column`_'with""_quotes",
    _airbyte_emitted_at,
    _airbyte_partition_hashid
from __dbt__CTE__nested_stream_with_complex_columns_resulting_into_long_names_partition_ab3
-- partition at nested_stream_with_complex_columns_resulting_into_long_names/partition from "integrationtests".test_normalization."nested_stream_with_complex_columns_resulting_into_long_names"
  );