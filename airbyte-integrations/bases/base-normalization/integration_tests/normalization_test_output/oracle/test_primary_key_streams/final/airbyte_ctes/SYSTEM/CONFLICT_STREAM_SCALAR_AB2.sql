
  create view SYSTEM.CONFLICT_STREAM_SCALAR_AB2__dbt_tmp as
    
-- SQL model to cast each column to its adequate SQL type converted from the JSON schema type
select
    cast(ID as varchar(1000)) as ID,
    cast(CONFLICT_STREAM_SCALAR as 
    numeric
) as CONFLICT_STREAM_SCALAR,
    airbyte_emitted_at
from SYSTEM.CONFLICT_STREAM_SCALAR_AB1
-- CONFLICT_STREAM_SCALAR

