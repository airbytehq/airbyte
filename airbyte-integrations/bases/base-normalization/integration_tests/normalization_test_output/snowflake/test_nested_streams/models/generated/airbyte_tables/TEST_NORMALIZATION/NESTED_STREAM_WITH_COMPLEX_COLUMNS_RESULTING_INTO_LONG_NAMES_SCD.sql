{{ config(schema="TEST_NORMALIZATION", tags=["top-level"]) }}
-- SQL model to build a Type 2 Slowly Changing Dimension (SCD) table for each record identified by their primary key
select
    ID,
    DATE,
    PARTITION,
  DATE as _AIRBYTE_START_AT,
  lag(DATE) over (
    partition by ID
    order by DATE is null asc, DATE desc, _AIRBYTE_EMITTED_AT desc
  ) as _AIRBYTE_END_AT,
  case when lag(DATE) over (
    partition by ID
    order by DATE is null asc, DATE desc, _AIRBYTE_EMITTED_AT desc
  ) is null  then 1 else 0 end as _AIRBYTE_ACTIVE_ROW,
  _AIRBYTE_EMITTED_AT,
  _AIRBYTE_NESTED_STREAM_WITH_COMPLEX_COLUMNS_RESULTING_INTO_LONG_NAMES_HASHID
from {{ ref('NESTED_STREAM_WITH_COMPLEX_COLUMNS_RESULTING_INTO_LONG_NAMES_AB4') }}
-- NESTED_STREAM_WITH_COMPLEX_COLUMNS_RESULTING_INTO_LONG_NAMES from {{ source('TEST_NORMALIZATION', '_AIRBYTE_RAW_NESTED_STREAM_WITH_COMPLEX_COLUMNS_RESULTING_INTO_LONG_NAMES') }}
where _airbyte_row_num = 1

