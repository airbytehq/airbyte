

      create or replace transient table "AIRBYTE_DATABASE".TEST_NORMALIZATION."DEDUP_CDC_EXCLUDED_SCD"  as
      (
-- SQL model to build a Type 2 Slowly Changing Dimension (SCD) table for each record identified by their primary key
select
    ID,
    NAME,
    _AB_CDC_LSN,
    _AB_CDC_UPDATED_AT,
    _AB_CDC_DELETED_AT,
    _airbyte_emitted_at as _airbyte_start_at,
    lag(_airbyte_emitted_at) over (
        partition by ID
        order by _airbyte_emitted_at is null asc, _airbyte_emitted_at desc, _airbyte_emitted_at desc
    ) as _airbyte_end_at,
    lag(_airbyte_emitted_at) over (
        partition by ID
        order by _airbyte_emitted_at is null asc, _airbyte_emitted_at desc, _airbyte_emitted_at desc, _ab_cdc_updated_at desc
    ) is null and _ab_cdc_deleted_at is null as _airbyte_active_row,
    _airbyte_emitted_at,
    _AIRBYTE_DEDUP_CDC_EXCLUDED_HASHID
from "AIRBYTE_DATABASE"._AIRBYTE_TEST_NORMALIZATION."DEDUP_CDC_EXCLUDED_AB4"
-- DEDUP_CDC_EXCLUDED from "AIRBYTE_DATABASE".TEST_NORMALIZATION._AIRBYTE_RAW_DEDUP_CDC_EXCLUDED
where _airbyte_row_num = 1
      );
    