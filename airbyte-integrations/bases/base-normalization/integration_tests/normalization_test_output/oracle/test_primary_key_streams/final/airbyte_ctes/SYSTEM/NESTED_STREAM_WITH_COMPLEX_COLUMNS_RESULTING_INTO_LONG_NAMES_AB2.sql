
  create view SYSTEM.NESTED_STREAM_WITH_COMPLEX_COLUMNS_RESULTING_INTO_LONG_NAMES_AB2__dbt_tmp as
    
-- SQL model to cast each column to its adequate SQL type converted from the JSON schema type
select
    cast(ID as varchar(1000)) as ID,
    cast("DATE" as varchar(1000)) as "DATE",
    cast(PARTITION as varchar2(3000)) as PARTITION,
    airbyte_emitted_at
from SYSTEM.NESTED_STREAM_WITH_COMPLEX_COLUMNS_RESULTING_INTO_LONG_NAMES_AB1
-- NESTED_STREAM_WITH_COMPLEX_COLUMNS_RESULTING_INTO_LONG_NAMES

