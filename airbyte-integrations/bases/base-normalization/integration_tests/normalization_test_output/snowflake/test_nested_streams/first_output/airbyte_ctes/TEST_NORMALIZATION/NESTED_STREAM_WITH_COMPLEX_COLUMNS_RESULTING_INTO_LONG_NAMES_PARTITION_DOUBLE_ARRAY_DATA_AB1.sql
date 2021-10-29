
  create or replace  view "AIRBYTE_DATABASE"._AIRBYTE_TEST_NORMALIZATION."NESTED_STREAM_WITH_COMPLEX_COLUMNS_RESULTING_INTO_LONG_NAMES_PARTITION_DOUBLE_ARRAY_DATA_AB1"  as (
    
-- SQL model to parse JSON blob stored in a single column and extract into separated field columns as described by the JSON Schema

select
    _AIRBYTE_PARTITION_HASHID,
    to_varchar(get_path(parse_json(DOUBLE_ARRAY_DATA.value), '"id"')) as ID,
    _AIRBYTE_AB_ID,
    _AIRBYTE_EMITTED_AT,
    convert_timezone('UTC', current_timestamp()) as _AIRBYTE_NORMALIZED_AT
from "AIRBYTE_DATABASE".TEST_NORMALIZATION."NESTED_STREAM_WITH_COMPLEX_COLUMNS_RESULTING_INTO_LONG_NAMES_PARTITION" as table_alias
-- DOUBLE_ARRAY_DATA at nested_stream_with_complex_columns_resulting_into_long_names/partition/double_array_data
cross join table(flatten(DOUBLE_ARRAY_DATA)) as DOUBLE_ARRAY_DATA
where 1 = 1
and DOUBLE_ARRAY_DATA is not null
  );
