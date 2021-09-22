

  create or replace table `dataline-integration-testing`.test_normalization.`nested_stream_with_complex_columns_resulting_into_long_names_partition_DATA`
  
  
  OPTIONS()
  as (
    
with __dbt__CTE__nested_stream_with_complex_columns_resulting_into_long_names_partition_DATA_ab1 as (

-- SQL model to parse JSON blob stored in a single column and extract into separated field columns as described by the JSON Schema

select
    _airbyte_partition_hashid,
    json_extract_scalar(DATA, "$['currency']") as currency,
    _airbyte_emitted_at
from `dataline-integration-testing`.test_normalization.`nested_stream_with_complex_columns_resulting_into_long_names_partition` as table_alias
cross join unnest(DATA) as DATA
where DATA is not null
-- DATA at nested_stream_with_complex_columns_resulting_into_long_names/partition/DATA
),  __dbt__CTE__nested_stream_with_complex_columns_resulting_into_long_names_partition_DATA_ab2 as (

-- SQL model to cast each column to its adequate SQL type converted from the JSON schema type
select
    _airbyte_partition_hashid,
    cast(currency as 
    string
) as currency,
    _airbyte_emitted_at
from __dbt__CTE__nested_stream_with_complex_columns_resulting_into_long_names_partition_DATA_ab1
-- DATA at nested_stream_with_complex_columns_resulting_into_long_names/partition/DATA
),  __dbt__CTE__nested_stream_with_complex_columns_resulting_into_long_names_partition_DATA_ab3 as (

-- SQL model to build a hash column based on the values of this record
select
    to_hex(md5(cast(concat(coalesce(cast(_airbyte_partition_hashid as 
    string
), ''), '-', coalesce(cast(currency as 
    string
), '')) as 
    string
))) as _airbyte_DATA_hashid,
    tmp.*
from __dbt__CTE__nested_stream_with_complex_columns_resulting_into_long_names_partition_DATA_ab2 tmp
-- DATA at nested_stream_with_complex_columns_resulting_into_long_names/partition/DATA
)-- Final base SQL model
select
    _airbyte_partition_hashid,
    currency,
    _airbyte_emitted_at,
    _airbyte_DATA_hashid
from __dbt__CTE__nested_stream_with_complex_columns_resulting_into_long_names_partition_DATA_ab3
-- DATA at nested_stream_with_complex_columns_resulting_into_long_names/partition/DATA from `dataline-integration-testing`.test_normalization.`nested_stream_with_complex_columns_resulting_into_long_names_partition`
  );
    