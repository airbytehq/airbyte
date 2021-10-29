
  create or replace  view "AIRBYTE_DATABASE"._AIRBYTE_TEST_NORMALIZATION."NESTED_STREAM_WITH_COMPLEX_COLUMNS_RESULTING_INTO_LONG_NAMES_PARTITION_AB1"  as (
    
-- SQL model to parse JSON blob stored in a single column and extract into separated field columns as described by the JSON Schema
select
    _AIRBYTE_NESTED_STREAM_WITH_COMPLEX_COLUMNS_RESULTING_INTO_LONG_NAMES_HASHID,
    get_path(parse_json(PARTITION), '"double_array_data"') as DOUBLE_ARRAY_DATA,
    get_path(parse_json(PARTITION), '"DATA"') as DATA,
    get_path(parse_json(PARTITION), '"column`_''with""_quotes"') as "column`_'with""_quotes",
    _AIRBYTE_AB_ID,
    _AIRBYTE_EMITTED_AT,
    convert_timezone('UTC', current_timestamp()) as _AIRBYTE_NORMALIZED_AT
from "AIRBYTE_DATABASE".TEST_NORMALIZATION."NESTED_STREAM_WITH_COMPLEX_COLUMNS_RESULTING_INTO_LONG_NAMES" as table_alias
-- PARTITION at nested_stream_with_complex_columns_resulting_into_long_names/partition
where 1 = 1
and PARTITION is not null
  );
