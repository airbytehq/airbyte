

      create or replace transient table "AIRBYTE_DATABASE".TEST_NORMALIZATION."POS_DEDUP_CDCX_SCD"  as
      (
-- SQL model to build a Type 2 Slowly Changing Dimension (SCD) table for each record identified by their primary key
select
    ID,
    NAME,
    _AB_CDC_LSN,
    _AB_CDC_UPDATED_AT,
    _AB_CDC_DELETED_AT,
    _AB_CDC_LOG_POS,
  _AIRBYTE_EMITTED_AT as _AIRBYTE_START_AT,
  lag(_AIRBYTE_EMITTED_AT) over (
    partition by ID
    order by _AIRBYTE_EMITTED_AT is null asc, _AIRBYTE_EMITTED_AT desc, _AIRBYTE_EMITTED_AT desc
  ) as _AIRBYTE_END_AT,
  case when lag(_AIRBYTE_EMITTED_AT) over (
    partition by ID
    order by _AIRBYTE_EMITTED_AT is null asc, _AIRBYTE_EMITTED_AT desc, _AIRBYTE_EMITTED_AT desc, _AB_CDC_UPDATED_AT desc, _AB_CDC_LOG_POS desc
  ) is null and _AB_CDC_DELETED_AT is null  then 1 else 0 end as _AIRBYTE_ACTIVE_ROW,
  _AIRBYTE_EMITTED_AT,
  _AIRBYTE_POS_DEDUP_CDCX_HASHID
from "AIRBYTE_DATABASE"._AIRBYTE_TEST_NORMALIZATION."POS_DEDUP_CDCX_AB4"
-- POS_DEDUP_CDCX from "AIRBYTE_DATABASE".TEST_NORMALIZATION._AIRBYTE_RAW_POS_DEDUP_CDCX
where _airbyte_row_num = 1
      );
    