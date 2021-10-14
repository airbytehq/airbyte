USE [test_normalization];
    execute('create view _airbyte_test_normalization."nested_stream_with_co__column___with__quotes_ab2__dbt_tmp" as
    
-- SQL model to cast each column to its adequate SQL type converted from the JSON schema type
select
    _airbyte_partition_hashid,
    cast(currency as 
    VARCHAR(max)) as currency,
    _airbyte_emitted_at
from "test_normalization"._airbyte_test_normalization."nested_stream_with_co__column___with__quotes_ab1"
-- column___with__quotes at nested_stream_with_complex_columns_resulting_into_long_names/partition/column`_''with"_quotes
    ');

