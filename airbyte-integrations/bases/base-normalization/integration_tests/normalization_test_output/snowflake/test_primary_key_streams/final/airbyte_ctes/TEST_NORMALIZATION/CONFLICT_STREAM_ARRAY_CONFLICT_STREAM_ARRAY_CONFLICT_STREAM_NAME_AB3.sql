
  create or replace  view "AIRBYTE_DATABASE"._AIRBYTE_TEST_NORMALIZATION."CONFLICT_STREAM_ARRAY_CONFLICT_STREAM_ARRAY_CONFLICT_STREAM_NAME_AB3"  as (
    
-- SQL model to build a hash column based on the values of this record
select
    *,
    md5(cast(
    
    coalesce(cast(_AIRBYTE_CONFLICT_STREAM_ARRAY_2_HASHID as 
    varchar
), '') || '-' || coalesce(cast(ID as 
    varchar
), '')

 as 
    varchar
)) as _AIRBYTE_CONFLICT_STREAM_NAME_HASHID
from "AIRBYTE_DATABASE"._AIRBYTE_TEST_NORMALIZATION."CONFLICT_STREAM_ARRAY_CONFLICT_STREAM_ARRAY_CONFLICT_STREAM_NAME_AB2"
-- CONFLICT_STREAM_NAME at conflict_stream_array/conflict_stream_array/conflict_stream_name
  );
