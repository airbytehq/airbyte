

  create or replace view `dataline-integration-testing`._airbyte_test_normalization.`dedup_cdc_excluded_ab1`
  OPTIONS()
  as 
-- SQL model to parse JSON blob stored in a single column and extract into separated field columns as described by the JSON Schema
select
    json_extract_scalar(_airbyte_data, "$['id']") as id,
    json_extract_scalar(_airbyte_data, "$['name']") as name,
    json_extract_scalar(_airbyte_data, "$['_ab_cdc_lsn']") as _ab_cdc_lsn,
    json_extract_scalar(_airbyte_data, "$['_ab_cdc_updated_at']") as _ab_cdc_updated_at,
    json_extract_scalar(_airbyte_data, "$['_ab_cdc_deleted_at']") as _ab_cdc_deleted_at,
    _airbyte_emitted_at
from `dataline-integration-testing`.test_normalization._airbyte_raw_dedup_cdc_excluded as table_alias
-- dedup_cdc_excluded;

