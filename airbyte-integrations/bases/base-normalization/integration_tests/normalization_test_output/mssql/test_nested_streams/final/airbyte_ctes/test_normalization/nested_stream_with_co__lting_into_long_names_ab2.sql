USE [test_normalization];
    execute('create view _airbyte_test_normalization."nested_stream_with_co__lting_into_long_names_ab2__dbt_tmp" as
    
-- SQL model to cast each column to its adequate SQL type converted from the JSON schema type
select
    cast(id as 
    VARCHAR(max)) as id,
    cast("date" as 
    VARCHAR(max)) as "date",
    cast("partition" as VARCHAR(max)) as "partition",
    _airbyte_emitted_at
from "test_normalization"._airbyte_test_normalization."nested_stream_with_co__lting_into_long_names_ab1"
-- nested_stream_with_co__lting_into_long_names
    ');

