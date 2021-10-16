
  create view _airbyte_test_normalization.`pos_dedup_cdcx_ab1__dbt_tmp` as (
    
-- SQL model to parse JSON blob stored in a single column and extract into separated field columns as described by the JSON Schema
select
    json_value(_airbyte_data, 
    '$."id"') as id,
    json_value(_airbyte_data, 
    '$."name"') as `name`,
    json_value(_airbyte_data, 
    '$."_ab_cdc_lsn"') as _ab_cdc_lsn,
    json_value(_airbyte_data, 
    '$."_ab_cdc_updated_at"') as _ab_cdc_updated_at,
    json_value(_airbyte_data, 
    '$."_ab_cdc_deleted_at"') as _ab_cdc_deleted_at,
    json_value(_airbyte_data, 
    '$."_ab_cdc_log_pos"') as _ab_cdc_log_pos,
    _airbyte_emitted_at
from test_normalization._airbyte_raw_pos_dedup_cdcx as table_alias
-- pos_dedup_cdcx
  );
