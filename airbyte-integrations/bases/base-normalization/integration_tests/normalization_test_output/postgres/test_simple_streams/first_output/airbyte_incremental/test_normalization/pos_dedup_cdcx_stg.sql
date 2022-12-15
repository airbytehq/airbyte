
      

  create  table "postgres"._airbyte_test_normalization."pos_dedup_cdcx_stg"
  as (
    
with __dbt__cte__pos_dedup_cdcx_ab1 as (

-- SQL model to parse JSON blob stored in a single column and extract into separated field columns as described by the JSON Schema
-- depends_on: "postgres".test_normalization._airbyte_raw_pos_dedup_cdcx
select
    jsonb_extract_path_text(_airbyte_data, 'id') as "id",
    jsonb_extract_path_text(_airbyte_data, 'name') as "name",
    jsonb_extract_path_text(_airbyte_data, '_ab_cdc_lsn') as _ab_cdc_lsn,
    jsonb_extract_path_text(_airbyte_data, '_ab_cdc_updated_at') as _ab_cdc_updated_at,
    jsonb_extract_path_text(_airbyte_data, '_ab_cdc_deleted_at') as _ab_cdc_deleted_at,
    jsonb_extract_path_text(_airbyte_data, '_ab_cdc_log_pos') as _ab_cdc_log_pos,
    _airbyte_ab_id,
    _airbyte_emitted_at,
    now() as _airbyte_normalized_at
from "postgres".test_normalization._airbyte_raw_pos_dedup_cdcx as table_alias
-- pos_dedup_cdcx
where 1 = 1

),  __dbt__cte__pos_dedup_cdcx_ab2 as (

-- SQL model to cast each column to its adequate SQL type converted from the JSON schema type
-- depends_on: __dbt__cte__pos_dedup_cdcx_ab1
select
    cast("id" as 
    bigint
) as "id",
    cast("name" as text) as "name",
    cast(_ab_cdc_lsn as 
    float
) as _ab_cdc_lsn,
    cast(_ab_cdc_updated_at as 
    float
) as _ab_cdc_updated_at,
    cast(_ab_cdc_deleted_at as 
    float
) as _ab_cdc_deleted_at,
    cast(_ab_cdc_log_pos as 
    float
) as _ab_cdc_log_pos,
    _airbyte_ab_id,
    _airbyte_emitted_at,
    now() as _airbyte_normalized_at
from __dbt__cte__pos_dedup_cdcx_ab1
-- pos_dedup_cdcx
where 1 = 1

)-- SQL model to build a hash column based on the values of this record
-- depends_on: __dbt__cte__pos_dedup_cdcx_ab2
select
    md5(cast(coalesce(cast("id" as text), '') || '-' || coalesce(cast("name" as text), '') || '-' || coalesce(cast(_ab_cdc_lsn as text), '') || '-' || coalesce(cast(_ab_cdc_updated_at as text), '') || '-' || coalesce(cast(_ab_cdc_deleted_at as text), '') || '-' || coalesce(cast(_ab_cdc_log_pos as text), '') as text)) as _airbyte_pos_dedup_cdcx_hashid,
    tmp.*
from __dbt__cte__pos_dedup_cdcx_ab2 tmp
-- pos_dedup_cdcx
where 1 = 1

  );
  