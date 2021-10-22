
  create or replace  view "AIRBYTE_DATABASE"._AIRBYTE_TEST_NORMALIZATION."CONFLICT_STREAM_ARRAY_AB2"  as (
    
-- SQL model to cast each column to its adequate SQL type converted from the JSON schema type
select
    cast(ID as 
    varchar
) as ID,
    CONFLICT_STREAM_ARRAY,
    _AIRBYTE_EMITTED_AT
from "AIRBYTE_DATABASE"._AIRBYTE_TEST_NORMALIZATION."CONFLICT_STREAM_ARRAY_AB1"
-- CONFLICT_STREAM_ARRAY
  );
