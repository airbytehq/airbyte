

  create  table test_normalization.nested_stream_with_complex_columns_resulting_into_long_names_partition_data__dbt_tmp
  
  as
    
with dbt__cte__nested_stream_with_complex_columns_resulting_into_long_names_partition_data_ab1__ as (

-- SQL model to parse JSON blob stored in a single column and extract into separated field columns as described by the JSON Schema

select
    "_AIRBYTE_PARTITION_HASHID",
    json_value(data, '$."currency"') as currency,
    "_AIRBYTE_EMITTED_AT"
from test_normalization.nested_stream_with_complex_columns_resulting_into_long_names_partition 

where data is not null
-- data at nested_stream_with_complex_columns_resulting_into_long_names/partition/DATA
),  dbt__cte__nested_stream_with_complex_columns_resulting_into_long_names_partition_data_ab2__ as (

-- SQL model to cast each column to its adequate SQL type converted from the JSON schema type
select
    "_AIRBYTE_PARTITION_HASHID",
    cast(currency as varchar2(4000)) as currency,
    "_AIRBYTE_EMITTED_AT"
from dbt__cte__nested_stream_with_complex_columns_resulting_into_long_names_partition_data_ab1__
-- data at nested_stream_with_complex_columns_resulting_into_long_names/partition/DATA
),  dbt__cte__nested_stream_with_complex_columns_resulting_into_long_names_partition_data_ab3__ as (

-- SQL model to build a hash column based on the values of this record
select
    ora_hash(
            
                "_AIRBYTE_PARTITION_HASHID" || '~' ||
            
            
                currency
            
    ) as "_AIRBYTE_DATA_HASHID",
    tmp.*
from dbt__cte__nested_stream_with_complex_columns_resulting_into_long_names_partition_data_ab2__ tmp
-- data at nested_stream_with_complex_columns_resulting_into_long_names/partition/DATA
)-- Final base SQL model
select
    "_AIRBYTE_PARTITION_HASHID",
    currency,
    "_AIRBYTE_EMITTED_AT",
    "_AIRBYTE_DATA_HASHID"
from dbt__cte__nested_stream_with_complex_columns_resulting_into_long_names_partition_data_ab3__
-- data at nested_stream_with_complex_columns_resulting_into_long_names/partition/DATA from test_normalization.nested_stream_with_complex_columns_resulting_into_long_names_partition