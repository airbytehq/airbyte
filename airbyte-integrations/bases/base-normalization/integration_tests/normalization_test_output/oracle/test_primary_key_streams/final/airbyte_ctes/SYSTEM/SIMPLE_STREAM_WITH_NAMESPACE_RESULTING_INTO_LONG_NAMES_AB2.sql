
  create view SYSTEM.SIMPLE_STREAM_WITH_NAMESPACE_RESULTING_INTO_LONG_NAMES_AB2__dbt_tmp as
    
-- SQL model to cast each column to its adequate SQL type converted from the JSON schema type
select
    cast(ID as varchar(1000)) as ID,
    cast("DATE" as varchar(1000)) as "DATE",
    airbyte_emitted_at
from SYSTEM.SIMPLE_STREAM_WITH_NAMESPACE_RESULTING_INTO_LONG_NAMES_AB1
-- SIMPLE_STREAM_WITH_NAMESPACE_RESULTING_INTO_LONG_NAMES

