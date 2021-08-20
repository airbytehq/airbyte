
  create view SYSTEM.CONFLICT_STREAM_ARRAY_AB2__dbt_tmp as
    
-- SQL model to cast each column to its adequate SQL type converted from the JSON schema type
select
    cast(ID as varchar(1000)) as ID,
    cast(CONFLICT_STREAM_ARRAY as varchar2(3000)) as CONFLICT_STREAM_ARRAY,
    airbyte_emitted_at
from SYSTEM.CONFLICT_STREAM_ARRAY_AB1
-- CONFLICT_STREAM_ARRAY

