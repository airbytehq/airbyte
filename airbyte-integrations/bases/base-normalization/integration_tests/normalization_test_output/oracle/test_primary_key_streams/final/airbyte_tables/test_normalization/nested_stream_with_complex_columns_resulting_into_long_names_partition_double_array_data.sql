

  create  table test_normalization.nested_stream_with_complex_columns_resulting_into_long_names_partition_double_array_data__dbt_tmp
  
  as
    
with dbt__cte__nested_stream_with_complex_columns_resulting_into_long_names_partition_double_array_data_ab1__ as (

-- SQL model to parse JSON blob stored in a single column and extract into separated field columns as described by the JSON Schema

select
    "_AIRBYTE_PARTITION_HASHID",
    json_value(double_array_data, '$."id"') as id,
    "_AIRBYTE_EMITTED_AT"
from test_normalization.nested_stream_with_complex_columns_resulting_into_long_names_partition 

where double_array_data is not null
-- double_array_data at nested_stream_with_complex_columns_resulting_into_long_names/partition/double_array_data
),  dbt__cte__nested_stream_with_complex_columns_resulting_into_long_names_partition_double_array_data_ab2__ as (

-- SQL model to cast each column to its adequate SQL type converted from the JSON schema type
select
    "_AIRBYTE_PARTITION_HASHID",
    cast(id as varchar2(4000)) as id,
    "_AIRBYTE_EMITTED_AT"
from dbt__cte__nested_stream_with_complex_columns_resulting_into_long_names_partition_double_array_data_ab1__
-- double_array_data at nested_stream_with_complex_columns_resulting_into_long_names/partition/double_array_data
),  dbt__cte__nested_stream_with_complex_columns_resulting_into_long_names_partition_double_array_data_ab3__ as (

-- SQL model to build a hash column based on the values of this record
select
    ora_hash(
            
                "_AIRBYTE_PARTITION_HASHID" || '~' ||
            
            
                id
            
    ) as "_AIRBYTE_DOUBLE_ARRAY_DATA_HASHID",
    tmp.*
from dbt__cte__nested_stream_with_complex_columns_resulting_into_long_names_partition_double_array_data_ab2__ tmp
-- double_array_data at nested_stream_with_complex_columns_resulting_into_long_names/partition/double_array_data
)-- Final base SQL model
select
    "_AIRBYTE_PARTITION_HASHID",
    id,
    "_AIRBYTE_EMITTED_AT",
    "_AIRBYTE_DOUBLE_ARRAY_DATA_HASHID"
from dbt__cte__nested_stream_with_complex_columns_resulting_into_long_names_partition_double_array_data_ab3__
-- double_array_data at nested_stream_with_complex_columns_resulting_into_long_names/partition/double_array_data from test_normalization.nested_stream_with_complex_columns_resulting_into_long_names_partition