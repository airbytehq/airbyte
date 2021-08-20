
  create view SYSTEM.DEDUP_CDC_EXCLUDED_AB1__dbt_tmp as
    
-- SQL model to parse JSON blob stored in a single column and extract into separated field columns as described by the JSON Schema
select
    json_value(airbyte_data, '$."id"') as ID,
    json_value(airbyte_data, '$."name"') as NAME,
    json_value(airbyte_data, '$."_ab_cdc_lsn"') as "_AB_CDC_LSN",
    json_value(airbyte_data, '$."_ab_cdc_updated_at"') as "_AB_CDC_UPDATED_AT",
    json_value(airbyte_data, '$."_ab_cdc_deleted_at"') as "_AB_CDC_DELETED_AT",
    airbyte_emitted_at
from "SYSTEM"."AIRBYTE_RAW_DEDUP_CDC_EXCLUDED"
-- DEDUP_CDC_EXCLUDED

