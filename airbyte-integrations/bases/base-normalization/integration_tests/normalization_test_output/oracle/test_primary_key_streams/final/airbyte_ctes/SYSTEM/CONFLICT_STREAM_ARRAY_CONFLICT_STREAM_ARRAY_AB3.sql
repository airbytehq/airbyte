
  create view SYSTEM.CONFLICT_STREAM_ARRAY_CONFLICT_STREAM_ARRAY_AB3__dbt_tmp as
    
-- SQL model to build a hash column based on the values of this record
select
    ora_hash(
        'AIRBYTE_CONFLICT_STREAM_ARRAY_HASHID' || '~' ||
        cast(CONFLICT_STREAM_NAME as varchar(3000))
    ) as AIRBYTE_CONFLICT_STREAM_ARRAY_2_HASHID,
    tmp.*
from SYSTEM.CONFLICT_STREAM_ARRAY_CONFLICT_STREAM_ARRAY_AB2 tmp
-- CONFLICT_STREAM_ARRAY at conflict_stream_array/conflict_stream_array

