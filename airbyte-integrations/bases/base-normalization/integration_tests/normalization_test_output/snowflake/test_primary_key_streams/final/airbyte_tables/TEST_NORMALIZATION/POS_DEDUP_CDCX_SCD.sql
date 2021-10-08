

      create or replace transient table "AIRBYTE_DATABASE".TEST_NORMALIZATION."POS_DEDUP_CDCX_SCD"  as
      (
with __dbt__CTE__POS_DEDUP_CDCX_AB1 as (

-- SQL model to parse JSON blob stored in a single column and extract into separated field columns as described by the JSON Schema
select
    to_varchar(get_path(parse_json(_airbyte_data), '"id"')) as ID,
    to_varchar(get_path(parse_json(_airbyte_data), '"name"')) as NAME,
    to_varchar(get_path(parse_json(_airbyte_data), '"_ab_cdc_lsn"')) as _AB_CDC_LSN,
    to_varchar(get_path(parse_json(_airbyte_data), '"_ab_cdc_updated_at"')) as _AB_CDC_UPDATED_AT,
    to_varchar(get_path(parse_json(_airbyte_data), '"_ab_cdc_deleted_at"')) as _AB_CDC_DELETED_AT,
    to_varchar(get_path(parse_json(_airbyte_data), '"_ab_cdc_log_pos"')) as _AB_CDC_LOG_POS,
    _AIRBYTE_EMITTED_AT
from "AIRBYTE_DATABASE".TEST_NORMALIZATION._AIRBYTE_RAW_POS_DEDUP_CDCX as table_alias
-- POS_DEDUP_CDCX
),  __dbt__CTE__POS_DEDUP_CDCX_AB2 as (

-- SQL model to cast each column to its adequate SQL type converted from the JSON schema type
select
    cast(ID as 
    bigint
) as ID,
    cast(NAME as 
    varchar
) as NAME,
    cast(_AB_CDC_LSN as 
    float
) as _AB_CDC_LSN,
    cast(_AB_CDC_UPDATED_AT as 
    float
) as _AB_CDC_UPDATED_AT,
    cast(_AB_CDC_DELETED_AT as 
    float
) as _AB_CDC_DELETED_AT,
    cast(_AB_CDC_LOG_POS as 
    float
) as _AB_CDC_LOG_POS,
    _AIRBYTE_EMITTED_AT
from __dbt__CTE__POS_DEDUP_CDCX_AB1
-- POS_DEDUP_CDCX
),  __dbt__CTE__POS_DEDUP_CDCX_AB3 as (

-- SQL model to build a hash column based on the values of this record
select
    md5(cast(
    
    coalesce(cast(ID as 
    varchar
), '') || '-' || coalesce(cast(NAME as 
    varchar
), '') || '-' || coalesce(cast(_AB_CDC_LSN as 
    varchar
), '') || '-' || coalesce(cast(_AB_CDC_UPDATED_AT as 
    varchar
), '') || '-' || coalesce(cast(_AB_CDC_DELETED_AT as 
    varchar
), '') || '-' || coalesce(cast(_AB_CDC_LOG_POS as 
    varchar
), '')

 as 
    varchar
)) as _AIRBYTE_POS_DEDUP_CDCX_HASHID,
    tmp.*
from __dbt__CTE__POS_DEDUP_CDCX_AB2 tmp
-- POS_DEDUP_CDCX
),  __dbt__CTE__POS_DEDUP_CDCX_AB4 as (

-- SQL model to prepare for deduplicating records based on the hash record column
select
  row_number() over (
    partition by _AIRBYTE_POS_DEDUP_CDCX_HASHID
    order by _AIRBYTE_EMITTED_AT asc
  ) as _AIRBYTE_ROW_NUM,
  tmp.*
from __dbt__CTE__POS_DEDUP_CDCX_AB3 tmp
-- POS_DEDUP_CDCX from "AIRBYTE_DATABASE".TEST_NORMALIZATION._AIRBYTE_RAW_POS_DEDUP_CDCX
)-- SQL model to build a Type 2 Slowly Changing Dimension (SCD) table for each record identified by their primary key
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
from __dbt__CTE__POS_DEDUP_CDCX_AB4
-- POS_DEDUP_CDCX from "AIRBYTE_DATABASE".TEST_NORMALIZATION._AIRBYTE_RAW_POS_DEDUP_CDCX
where _airbyte_row_num = 1
      );
    