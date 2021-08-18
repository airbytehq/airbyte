
  create view "postgres"._airbyte_test_normalization."dedup_cdc_excluded_ab1__dbt_tmp" as (
    
-- SQL model to parse JSON blob stored in a single column and extract into separated field columns as described by the JSON Schema
select
    jsonb_extract_path_text(_airbyte_data, 'id') as "id",
    jsonb_extract_path_text(_airbyte_data, 'name') as "name",
    jsonb_extract_path_text(_airbyte_data, '_ab_cdc_lsn') as _ab_cdc_lsn,
    jsonb_extract_path_text(_airbyte_data, '_ab_cdc_updated_at') as _ab_cdc_updated_at,
    jsonb_extract_path_text(_airbyte_data, '_ab_cdc_deleted_at') as _ab_cdc_deleted_at,
    _airbyte_emitted_at
from "postgres".test_normalization._airbyte_raw_dedup_cdc_excluded as table_alias
-- dedup_cdc_excluded
  );
