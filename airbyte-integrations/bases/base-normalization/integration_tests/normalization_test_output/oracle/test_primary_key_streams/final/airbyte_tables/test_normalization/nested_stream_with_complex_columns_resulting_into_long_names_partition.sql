

  create  table test_normalization.nested_stream_with_complex_columns_resulting_into_long_names_partition__dbt_tmp
  
  as
    
with dbt__cte__nested_stream_with_complex_columns_resulting_into_long_names_partition_ab1__ as (

-- SQL model to parse JSON blob stored in a single column and extract into separated field columns as described by the JSON Schema
select
    "_AIRBYTE_NESTED_STREAM_WITH_COMPLEX_COLUMNS_RESULTING_INTO_LONG_NAMES_HASHID",
    json_value(partition, '$."double_array_data"') as double_array_data,
    json_value(partition, '$."DATA"') as data,
    json_value(partition, '$."column___with__quotes"') as column___with__quotes,
    "_AIRBYTE_EMITTED_AT"
from test_normalization.nested_stream_with_complex_columns_resulting_into_long_names 
where partition is not null
-- partition at nested_stream_with_complex_columns_resulting_into_long_names/partition
),  dbt__cte__nested_stream_with_complex_columns_resulting_into_long_names_partition_ab2__ as (

-- SQL model to cast each column to its adequate SQL type converted from the JSON schema type
select
    "_AIRBYTE_NESTED_STREAM_WITH_COMPLEX_COLUMNS_RESULTING_INTO_LONG_NAMES_HASHID",
    double_array_data,
    data,
    column___with__quotes,
    "_AIRBYTE_EMITTED_AT"
from dbt__cte__nested_stream_with_complex_columns_resulting_into_long_names_partition_ab1__
-- partition at nested_stream_with_complex_columns_resulting_into_long_names/partition
),  dbt__cte__nested_stream_with_complex_columns_resulting_into_long_names_partition_ab3__ as (

-- SQL model to build a hash column based on the values of this record
select
    ora_hash(
            
                "_AIRBYTE_NESTED_STREAM_WITH_COMPLEX_COLUMNS_RESULTING_INTO_LONG_NAMES_HASHID" || '~' ||
            
            
                cast(double_array_data as varchar2(4000)) || '~' ||
            
            
                cast(data as varchar2(4000)) || '~' ||
            
            
                cast(column___with__quotes as varchar2(4000))
            
    ) as "_AIRBYTE_PARTITION_HASHID",
    tmp.*
from dbt__cte__nested_stream_with_complex_columns_resulting_into_long_names_partition_ab2__ tmp
-- partition at nested_stream_with_complex_columns_resulting_into_long_names/partition
)-- Final base SQL model
select
    "_AIRBYTE_NESTED_STREAM_WITH_COMPLEX_COLUMNS_RESULTING_INTO_LONG_NAMES_HASHID",
    double_array_data,
    data,
    column___with__quotes,
    "_AIRBYTE_EMITTED_AT",
    "_AIRBYTE_PARTITION_HASHID"
from dbt__cte__nested_stream_with_complex_columns_resulting_into_long_names_partition_ab3__
-- partition at nested_stream_with_complex_columns_resulting_into_long_names/partition from test_normalization.nested_stream_with_complex_columns_resulting_into_long_names