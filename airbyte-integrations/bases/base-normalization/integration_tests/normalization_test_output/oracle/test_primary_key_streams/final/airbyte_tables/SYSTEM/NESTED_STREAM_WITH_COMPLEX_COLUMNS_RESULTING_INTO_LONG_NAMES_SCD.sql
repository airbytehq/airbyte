

  create  table SYSTEM.NESTED_STREAM_WITH_COMPLEX_COLUMNS_RESULTING_INTO_LONG_NAMES_SCD__dbt_tmp
  
  as
    
-- SQL model to build a Type 2 Slowly Changing Dimension (SCD) table for each record identified by their primary key
select
    ID,
    "DATE",
    PARTITION,
    "DATE" as airbyte_start_at,
    lag("DATE") over (
        partition by ID
        order by "DATE" desc, airbyte_emitted_at desc
    ) as airbyte_end_at,
    coalesce(cast(lag("DATE") over (
        partition by ID
        order by "DATE" desc, airbyte_emitted_at desc
    ) as varchar(200)), 'Latest') as airbyte_active_row,
    airbyte_emitted_at,
    AIRBYTE_NESTED_STREAM_WITH_COMPLEX_COLUMNS_RESULTING_INTO_LONG_NAMES_HASHID
from SYSTEM.NESTED_STREAM_WITH_COMPLEX_COLUMNS_RESULTING_INTO_LONG_NAMES_AB4
-- NESTED_STREAM_WITH_COMPLEX_COLUMNS_RESULTING_INTO_LONG_NAMES from "SYSTEM"."AIRBYTE_RAW_NESTED_STREAM_WITH_COMPLEX_COLUMNS_RESULTING_INTO_LONG_NAMES"
where airbyte_row_num = 1