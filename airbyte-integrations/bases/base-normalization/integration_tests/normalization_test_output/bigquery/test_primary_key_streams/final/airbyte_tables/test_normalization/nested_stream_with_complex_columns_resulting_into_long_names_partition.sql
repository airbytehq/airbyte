

  create or replace table `dataline-integration-testing`.test_normalization.`nested_stream_with_complex_columns_resulting_into_long_names_partition`
  
  
  OPTIONS()
  as (
    
with __dbt__CTE__nested_stream_with_complex_columns_resulting_into_long_names_partition_ab1 as (

-- SQL model to parse JSON blob stored in a single column and extract into separated field columns as described by the JSON Schema
select
    _airbyte_nested_stream_with_complex_columns_resulting_into_long_names_hashid,
    json_extract_array(`partition`, "$['double_array_data']") as double_array_data,
    json_extract_array(`partition`, "$['DATA']") as DATA,
    json_extract_array(`partition`, "$['column___with__quotes']") as column___with__quotes,
    _airbyte_emitted_at
from `dataline-integration-testing`.test_normalization.`nested_stream_with_complex_columns_resulting_into_long_names` as table_alias
where `partition` is not null
-- partition at nested_stream_with_complex_columns_resulting_into_long_names/partition
),  __dbt__CTE__nested_stream_with_complex_columns_resulting_into_long_names_partition_ab2 as (

-- SQL model to cast each column to its adequate SQL type converted from the JSON schema type
select
    _airbyte_nested_stream_with_complex_columns_resulting_into_long_names_hashid,
    double_array_data,
    DATA,
    column___with__quotes,
    _airbyte_emitted_at
from __dbt__CTE__nested_stream_with_complex_columns_resulting_into_long_names_partition_ab1
-- partition at nested_stream_with_complex_columns_resulting_into_long_names/partition
),  __dbt__CTE__nested_stream_with_complex_columns_resulting_into_long_names_partition_ab3 as (

-- SQL model to build a hash column based on the values of this record
select
    to_hex(md5(cast(concat(coalesce(cast(_airbyte_nested_stream_with_complex_columns_resulting_into_long_names_hashid as 
    string
), ''), '-', coalesce(cast(array_to_string(double_array_data, "|", "") as 
    string
), ''), '-', coalesce(cast(array_to_string(DATA, "|", "") as 
    string
), ''), '-', coalesce(cast(array_to_string(column___with__quotes, "|", "") as 
    string
), '')) as 
    string
))) as _airbyte_partition_hashid,
    tmp.*
from __dbt__CTE__nested_stream_with_complex_columns_resulting_into_long_names_partition_ab2 tmp
-- partition at nested_stream_with_complex_columns_resulting_into_long_names/partition
)-- Final base SQL model
select
    _airbyte_nested_stream_with_complex_columns_resulting_into_long_names_hashid,
    double_array_data,
    DATA,
    column___with__quotes,
    _airbyte_emitted_at,
    _airbyte_partition_hashid
from __dbt__CTE__nested_stream_with_complex_columns_resulting_into_long_names_partition_ab3
-- partition at nested_stream_with_complex_columns_resulting_into_long_names/partition from `dataline-integration-testing`.test_normalization.`nested_stream_with_complex_columns_resulting_into_long_names`
  );
    