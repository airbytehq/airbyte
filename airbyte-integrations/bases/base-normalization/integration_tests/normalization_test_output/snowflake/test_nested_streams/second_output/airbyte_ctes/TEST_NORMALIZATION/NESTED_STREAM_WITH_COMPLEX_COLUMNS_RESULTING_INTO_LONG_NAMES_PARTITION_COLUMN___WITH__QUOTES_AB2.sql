
  create or replace  view "AIRBYTE_DATABASE"._AIRBYTE_TEST_NORMALIZATION."NESTED_STREAM_WITH_COMPLEX_COLUMNS_RESULTING_INTO_LONG_NAMES_PARTITION_COLUMN___WITH__QUOTES_AB2"  as (
    
-- SQL model to cast each column to its adequate SQL type converted from the JSON schema type
select
    _AIRBYTE_PARTITION_HASHID,
    cast(CURRENCY as 
    varchar
) as CURRENCY,
    _AIRBYTE_AB_ID,
    _AIRBYTE_EMITTED_AT,
    convert_timezone('UTC', current_timestamp()) as _AIRBYTE_NORMALIZED_AT
from "AIRBYTE_DATABASE"._AIRBYTE_TEST_NORMALIZATION."NESTED_STREAM_WITH_COMPLEX_COLUMNS_RESULTING_INTO_LONG_NAMES_PARTITION_COLUMN___WITH__QUOTES_AB1"
-- COLUMN___WITH__QUOTES at nested_stream_with_complex_columns_resulting_into_long_names/partition/column`_'with"_quotes
where 1 = 1
  );
