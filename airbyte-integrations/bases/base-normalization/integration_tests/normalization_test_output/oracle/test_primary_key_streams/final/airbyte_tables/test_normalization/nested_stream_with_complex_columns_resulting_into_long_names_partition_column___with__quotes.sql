

  create  table test_normalization.nested_stream_with_complex_columns_resulting_into_long_names_partition_column___with__quotes__dbt_tmp
  
  as
    
with dbt__cte__nested_stream_with_complex_columns_resulting_into_long_names_partition_column___with__quotes_ab1__ as (

-- SQL model to parse JSON blob stored in a single column and extract into separated field columns as described by the JSON Schema

select
    "_AIRBYTE_PARTITION_HASHID",
    json_value(column___with__quotes, '$."currency"') as currency,
    "_AIRBYTE_EMITTED_AT"
from test_normalization.nested_stream_with_complex_columns_resulting_into_long_names_partition 

where column___with__quotes is not null
-- column___with__quotes at nested_stream_with_complex_columns_resulting_into_long_names/partition/column`_'with"_quotes
),  dbt__cte__nested_stream_with_complex_columns_resulting_into_long_names_partition_column___with__quotes_ab2__ as (

-- SQL model to cast each column to its adequate SQL type converted from the JSON schema type
select
    "_AIRBYTE_PARTITION_HASHID",
    cast(currency as varchar2(4000)) as currency,
    "_AIRBYTE_EMITTED_AT"
from dbt__cte__nested_stream_with_complex_columns_resulting_into_long_names_partition_column___with__quotes_ab1__
-- column___with__quotes at nested_stream_with_complex_columns_resulting_into_long_names/partition/column`_'with"_quotes
),  dbt__cte__nested_stream_with_complex_columns_resulting_into_long_names_partition_column___with__quotes_ab3__ as (

-- SQL model to build a hash column based on the values of this record
select
    ora_hash(
            
                "_AIRBYTE_PARTITION_HASHID" || '~' ||
            
            
                currency
            
    ) as "_AIRBYTE_COLUMN___WITH__QUOTES_HASHID",
    tmp.*
from dbt__cte__nested_stream_with_complex_columns_resulting_into_long_names_partition_column___with__quotes_ab2__ tmp
-- column___with__quotes at nested_stream_with_complex_columns_resulting_into_long_names/partition/column`_'with"_quotes
)-- Final base SQL model
select
    "_AIRBYTE_PARTITION_HASHID",
    currency,
    "_AIRBYTE_EMITTED_AT",
    "_AIRBYTE_COLUMN___WITH__QUOTES_HASHID"
from dbt__cte__nested_stream_with_complex_columns_resulting_into_long_names_partition_column___with__quotes_ab3__
-- column___with__quotes at nested_stream_with_complex_columns_resulting_into_long_names/partition/column`_'with"_quotes from test_normalization.nested_stream_with_complex_columns_resulting_into_long_names_partition