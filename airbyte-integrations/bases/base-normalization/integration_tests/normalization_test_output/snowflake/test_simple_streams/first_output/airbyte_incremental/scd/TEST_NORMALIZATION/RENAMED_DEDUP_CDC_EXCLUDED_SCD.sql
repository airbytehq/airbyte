

      create or replace transient table "AIRBYTE_DATABASE".TEST_NORMALIZATION."RENAMED_DEDUP_CDC_EXCLUDED_SCD"  as
      (select * from(
            
with

input_data as (
    select *
    from "AIRBYTE_DATABASE"._AIRBYTE_TEST_NORMALIZATION."RENAMED_DEDUP_CDC_EXCLUDED_AB3"
    -- RENAMED_DEDUP_CDC_EXCLUDED from "AIRBYTE_DATABASE".TEST_NORMALIZATION._AIRBYTE_RAW_RENAMED_DEDUP_CDC_EXCLUDED
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
      _AIRBYTE_EMITTED_AT as _AIRBYTE_START_AT,
      lag(_AIRBYTE_EMITTED_AT) over (
        partition by ID
        order by
            _AIRBYTE_EMITTED_AT is null asc,
            _AIRBYTE_EMITTED_AT desc,
            _AIRBYTE_EMITTED_AT desc
      ) as _AIRBYTE_END_AT,
      case when lag(_AIRBYTE_EMITTED_AT) over (
        partition by ID
        order by
            _AIRBYTE_EMITTED_AT is null asc,
            _AIRBYTE_EMITTED_AT desc,
            _AIRBYTE_EMITTED_AT desc
      ) is null  then 1 else 0 end as _AIRBYTE_ACTIVE_ROW,
      _AIRBYTE_AB_ID,
      _AIRBYTE_EMITTED_AT,
      _AIRBYTE_RENAMED_DEDUP_CDC_EXCLUDED_HASHID
    from input_data
),
dedup_data as (
    select
        -- we need to ensure de-duplicated rows for merge/update queries
        -- additionally, we generate a unique key for the scd table
        row_number() over (
            partition by _AIRBYTE_UNIQUE_KEY, _AIRBYTE_START_AT, _AIRBYTE_EMITTED_AT
            order by _AIRBYTE_AB_ID
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
    _AIRBYTE_START_AT,
    _AIRBYTE_END_AT,
    _AIRBYTE_ACTIVE_ROW,
    _AIRBYTE_AB_ID,
    _AIRBYTE_EMITTED_AT,
    convert_timezone('UTC', current_timestamp()) as _AIRBYTE_NORMALIZED_AT,
    _AIRBYTE_RENAMED_DEDUP_CDC_EXCLUDED_HASHID
from dedup_data where _AIRBYTE_ROW_NUM = 1
            ) order by (_AIRBYTE_ACTIVE_ROW, _AIRBYTE_UNIQUE_KEY, _AIRBYTE_EMITTED_AT)
      );
    alter table "AIRBYTE_DATABASE".TEST_NORMALIZATION."RENAMED_DEDUP_CDC_EXCLUDED_SCD" cluster by (_AIRBYTE_ACTIVE_ROW, _AIRBYTE_UNIQUE_KEY, _AIRBYTE_EMITTED_AT);