

  create or replace view `dataline-integration-testing`._airbyte_test_normalization.`pos_dedup_cdcx_ab1`
  OPTIONS()
  as 
-- SQL model to parse JSON blob stored in a single column and extract into separated field columns as described by the JSON Schema
select
    json_extract_scalar(_airbyte_data, "$['id']") as id,
    json_extract_scalar(_airbyte_data, "$['name']") as name,
    json_extract_scalar(_airbyte_data, "$['_ab_cdc_lsn']") as _ab_cdc_lsn,
    json_extract_scalar(_airbyte_data, "$['_ab_cdc_updated_at']") as _ab_cdc_updated_at,
    json_extract_scalar(_airbyte_data, "$['_ab_cdc_deleted_at']") as _ab_cdc_deleted_at,
    json_extract_scalar(_airbyte_data, "$['_ab_cdc_log_pos']") as _ab_cdc_log_pos,
    _airbyte_emitted_at
from `dataline-integration-testing`.test_normalization._airbyte_raw_pos_dedup_cdcx as table_alias
-- pos_dedup_cdcx;

