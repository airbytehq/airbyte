
  create or replace  view "AIRBYTE_DATABASE"._AIRBYTE_TEST_NORMALIZATION."CONFLICT_STREAM_SCALAR_AB2"  as (
    
-- SQL model to cast each column to its adequate SQL type converted from the JSON schema type
select
    cast(ID as 
    varchar
) as ID,
    cast(CONFLICT_STREAM_SCALAR as 
    bigint
) as CONFLICT_STREAM_SCALAR,
    _AIRBYTE_AB_ID,
    _AIRBYTE_EMITTED_AT,
    convert_timezone('UTC', current_timestamp()) as _AIRBYTE_NORMALIZED_AT
from "AIRBYTE_DATABASE"._AIRBYTE_TEST_NORMALIZATION."CONFLICT_STREAM_SCALAR_AB1"
-- CONFLICT_STREAM_SCALAR
where 1 = 1
  );
