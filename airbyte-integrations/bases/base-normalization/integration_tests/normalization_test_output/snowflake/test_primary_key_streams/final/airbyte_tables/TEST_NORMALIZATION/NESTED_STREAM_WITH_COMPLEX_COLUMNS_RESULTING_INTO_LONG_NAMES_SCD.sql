

      create or replace transient table "AIRBYTE_DATABASE".TEST_NORMALIZATION."NESTED_STREAM_WITH_COMPLEX_COLUMNS_RESULTING_INTO_LONG_NAMES_SCD"  as
      (
-- SQL model to build a Type 2 Slowly Changing Dimension (SCD) table for each record identified by their primary key
select
    ID,
    DATE,
    PARTITION,
    DATE as _airbyte_start_at,
    lag(DATE) over (
        partition by ID
        order by DATE desc, _airbyte_emitted_at desc
    ) as _airbyte_end_at,
    lag(DATE) over (
        partition by ID
        order by DATE desc, _airbyte_emitted_at desc
    ) is null as _airbyte_active_row,
    _airbyte_emitted_at,
    _AIRBYTE_NESTED_STREAM_WITH_COMPLEX_COLUMNS_RESULTING_INTO_LONG_NAMES_HASHID
from "AIRBYTE_DATABASE"._AIRBYTE_TEST_NORMALIZATION."NESTED_STREAM_WITH_COMPLEX_COLUMNS_RESULTING_INTO_LONG_NAMES_AB4"
-- NESTED_STREAM_WITH_COMPLEX_COLUMNS_RESULTING_INTO_LONG_NAMES from "AIRBYTE_DATABASE".TEST_NORMALIZATION._AIRBYTE_RAW_NESTED_STREAM_WITH_COMPLEX_COLUMNS_RESULTING_INTO_LONG_NAMES
where _airbyte_row_num = 1
      );
    