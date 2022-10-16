

      create or replace  table "INTEGRATION_TEST_NORMALIZATION".TEST_NORMALIZATION."NESTED_STREAM_WITH_COMPLEX_COLUMNS_RESULTING_INTO_LONG_NAMES_SCD"  as
      (select * from(
            
-- depends_on: ref('NESTED_STREAM_WITH_COMPLEX_COLUMNS_RESULTING_INTO_LONG_NAMES_STG')
with

input_data as (
    select *
    from "INTEGRATION_TEST_NORMALIZATION"._AIRBYTE_TEST_NORMALIZATION."NESTED_STREAM_WITH_COMPLEX_COLUMNS_RESULTING_INTO_LONG_NAMES_STG"
    -- NESTED_STREAM_WITH_COMPLEX_COLUMNS_RESULTING_INTO_LONG_NAMES from "INTEGRATION_TEST_NORMALIZATION".TEST_NORMALIZATION._AIRBYTE_RAW_NESTED_STREAM_WITH_COMPLEX_COLUMNS_RESULTING_INTO_LONG_NAMES
),

scd_data as (
    -- SQL model to build a Type 2 Slowly Changing Dimension (SCD) table for each record identified by their primary key
    select
      md5(cast(coalesce(cast(ID as 
    varchar
), '') as 
    varchar
)) as _AIRBYTE_UNIQUE_KEY,
      ID,
      DATE,
      PARTITION,
      DATE as _AIRBYTE_START_AT,
      lag(DATE) over (
        partition by ID
        order by
            DATE is null asc,
            DATE desc,
            _AIRBYTE_EMITTED_AT desc
      ) as _AIRBYTE_END_AT,
      case when row_number() over (
        partition by ID
        order by
            DATE is null asc,
            DATE desc,
            _AIRBYTE_EMITTED_AT desc
      ) = 1 then 1 else 0 end as _AIRBYTE_ACTIVE_ROW,
      _AIRBYTE_AB_ID,
      _AIRBYTE_EMITTED_AT,
      _AIRBYTE_NESTED_STREAM_WITH_COMPLEX_COLUMNS_RESULTING_INTO_LONG_NAMES_HASHID
    from input_data
),
dedup_data as (
    select
        -- we need to ensure de-duplicated rows for merge/update queries
        -- additionally, we generate a unique key for the scd table
        row_number() over (
            partition by
                _AIRBYTE_UNIQUE_KEY,
                _AIRBYTE_START_AT,
                _AIRBYTE_EMITTED_AT
            order by _AIRBYTE_ACTIVE_ROW desc, _AIRBYTE_AB_ID
        ) as _AIRBYTE_ROW_NUM,
        md5(cast(coalesce(cast(_AIRBYTE_UNIQUE_KEY as 
    varchar
), '') || '-' || coalesce(cast(_AIRBYTE_START_AT as 
    varchar
), '') || '-' || coalesce(cast(_AIRBYTE_EMITTED_AT as 
    varchar
), '') as 
    varchar
)) as _AIRBYTE_UNIQUE_KEY_SCD,
        scd_data.*
    from scd_data
)
select
    _AIRBYTE_UNIQUE_KEY,
    _AIRBYTE_UNIQUE_KEY_SCD,
    ID,
    DATE,
    PARTITION,
    _AIRBYTE_START_AT,
    _AIRBYTE_END_AT,
    _AIRBYTE_ACTIVE_ROW,
    _AIRBYTE_AB_ID,
    _AIRBYTE_EMITTED_AT,
    convert_timezone('UTC', current_timestamp()) as _AIRBYTE_NORMALIZED_AT,
    _AIRBYTE_NESTED_STREAM_WITH_COMPLEX_COLUMNS_RESULTING_INTO_LONG_NAMES_HASHID
from dedup_data where _AIRBYTE_ROW_NUM = 1
            ) order by (_AIRBYTE_ACTIVE_ROW, _AIRBYTE_UNIQUE_KEY_SCD, _AIRBYTE_EMITTED_AT)
      );
    alter table "INTEGRATION_TEST_NORMALIZATION".TEST_NORMALIZATION."NESTED_STREAM_WITH_COMPLEX_COLUMNS_RESULTING_INTO_LONG_NAMES_SCD" cluster by (_AIRBYTE_ACTIVE_ROW, _AIRBYTE_UNIQUE_KEY_SCD, _AIRBYTE_EMITTED_AT);