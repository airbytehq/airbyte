USE [test_normalization];
    execute('create view _airbyte_test_normalization."nested_stream_with_co___long_names_partition_ab1__dbt_tmp" as
    
-- SQL model to parse JSON blob stored in a single column and extract into separated field columns as described by the JSON Schema
select
    _airbyte_nested_strea__nto_long_names_hashid,
    json_query("partition", ''$."double_array_data"'') as double_array_data,
    json_query("partition", ''$."DATA"'') as "DATA",
    json_query("partition", ''$."column`_''''with\"_quotes"'') as "column`_''with""_quotes",
    _airbyte_ab_id,
    _airbyte_emitted_at,
    SYSDATETIME() as _airbyte_normalized_at
from "test_normalization".test_normalization."nested_stream_with_co__lting_into_long_names" as table_alias
-- partition at nested_stream_with_complex_columns_resulting_into_long_names/partition
where 1 = 1
and "partition" is not null
    ');

