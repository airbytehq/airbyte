
  create or replace  view "AIRBYTE_DATABASE"._AIRBYTE_TEST_NORMALIZATION."DEDUP_CDC_EXCLUDED_AB1"  as (
    
-- SQL model to parse JSON blob stored in a single column and extract into separated field columns as described by the JSON Schema
select
    to_varchar(get_path(parse_json(_airbyte_data), '"id"')) as ID,
    to_varchar(get_path(parse_json(_airbyte_data), '"name"')) as NAME,
    to_varchar(get_path(parse_json(_airbyte_data), '"_ab_cdc_lsn"')) as _AB_CDC_LSN,
    to_varchar(get_path(parse_json(_airbyte_data), '"_ab_cdc_updated_at"')) as _AB_CDC_UPDATED_AT,
    to_varchar(get_path(parse_json(_airbyte_data), '"_ab_cdc_deleted_at"')) as _AB_CDC_DELETED_AT,
    _airbyte_emitted_at
from "AIRBYTE_DATABASE".TEST_NORMALIZATION._AIRBYTE_RAW_DEDUP_CDC_EXCLUDED as table_alias
-- DEDUP_CDC_EXCLUDED
  );
