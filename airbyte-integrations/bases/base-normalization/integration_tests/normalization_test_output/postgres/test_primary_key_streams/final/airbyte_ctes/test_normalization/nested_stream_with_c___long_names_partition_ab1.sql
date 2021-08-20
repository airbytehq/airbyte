
  create view "postgres"._airbyte_test_normalization."nested_stream_with_c___long_names_partition_ab1__dbt_tmp" as (
    
-- SQL model to parse JSON blob stored in a single column and extract into separated field columns as described by the JSON Schema
select
    _airbyte_nested_stre__nto_long_names_hashid,
    jsonb_extract_path("partition", 'double_array_data') as double_array_data,
    jsonb_extract_path("partition", 'DATA') as "DATA",
    jsonb_extract_path("partition", 'column`_''with"_quotes') as "column`_'with""_quotes",
    _airbyte_emitted_at
from "postgres".test_normalization."nested_stream_with_c__lting_into_long_names" as table_alias
where "partition" is not null
-- partition at nested_stream_with_complex_columns_resulting_into_long_names/partition
  );
