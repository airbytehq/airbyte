
  create or replace  view "AIRBYTE_DATABASE"._AIRBYTE_TEST_NORMALIZATION."NESTED_STREAM_WITH_COMPLEX_COLUMNS_RESULTING_INTO_LONG_NAMES_PARTITION_COLUMN___WITH__QUOTES_AB3"  as (
    
-- SQL model to build a hash column based on the values of this record
select
    md5(cast(coalesce(cast(_AIRBYTE_PARTITION_HASHID as 
    varchar
), '') || '-' || coalesce(cast(CURRENCY as 
    varchar
), '') as 
    varchar
)) as _AIRBYTE_COLUMN___WITH__QUOTES_HASHID,
    tmp.*
from "AIRBYTE_DATABASE"._AIRBYTE_TEST_NORMALIZATION."NESTED_STREAM_WITH_COMPLEX_COLUMNS_RESULTING_INTO_LONG_NAMES_PARTITION_COLUMN___WITH__QUOTES_AB2" tmp
-- COLUMN___WITH__QUOTES at nested_stream_with_complex_columns_resulting_into_long_names/partition/column`_'with"_quotes
  );
