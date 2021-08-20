
  create view SYSTEM.NESTED_STREAM_WITH_COMPLEX_COLUMNS_RESULTING_INTO_LONG_NAMES_PARTITION_AB1__dbt_tmp as
    
-- SQL model to parse JSON blob stored in a single column and extract into separated field columns as described by the JSON Schema
select
    AIRBYTE_NESTED_STREAM_WITH_COMPLEX_COLUMNS_RESULTING_INTO_LONG_NAMES_HASHID,
    json_value(PARTITION, '$."double_array_data"') as DOUBLE_ARRAY_DATA,
    json_value(PARTITION, '$."DATA"') as DATA,
    json_value(PARTITION, '$."column`_'with"_quotes"') as COLUMN___WITH__QUOTES,
    airbyte_emitted_at
from SYSTEM.NESTED_STREAM_WITH_COMPLEX_COLUMNS_RESULTING_INTO_LONG_NAMES
where PARTITION is not null
-- PARTITION at nested_stream_with_complex_columns_resulting_into_long_names/partition

