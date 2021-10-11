

  create  table
    "integrationtests".test_normalization."dedup_cdc_excluded_scd__dbt_tmp"
    
    
  as (
    
with __dbt__CTE__dedup_cdc_excluded_ab1 as (

-- SQL model to parse JSON blob stored in a single column and extract into separated field columns as described by the JSON Schema
select
    case when json_extract_path_text(_airbyte_data, 'id', true) != '' then json_extract_path_text(_airbyte_data, 'id', true) end as id,
    case when json_extract_path_text(_airbyte_data, 'name', true) != '' then json_extract_path_text(_airbyte_data, 'name', true) end as name,
    case when json_extract_path_text(_airbyte_data, '_ab_cdc_lsn', true) != '' then json_extract_path_text(_airbyte_data, '_ab_cdc_lsn', true) end as _ab_cdc_lsn,
    case when json_extract_path_text(_airbyte_data, '_ab_cdc_updated_at', true) != '' then json_extract_path_text(_airbyte_data, '_ab_cdc_updated_at', true) end as _ab_cdc_updated_at,
    case when json_extract_path_text(_airbyte_data, '_ab_cdc_deleted_at', true) != '' then json_extract_path_text(_airbyte_data, '_ab_cdc_deleted_at', true) end as _ab_cdc_deleted_at,
    _airbyte_emitted_at
from "integrationtests".test_normalization._airbyte_raw_dedup_cdc_excluded as table_alias
-- dedup_cdc_excluded
),  __dbt__CTE__dedup_cdc_excluded_ab2 as (

-- SQL model to cast each column to its adequate SQL type converted from the JSON schema type
select
    cast(id as 
    bigint
) as id,
    cast(name as varchar) as name,
    cast(_ab_cdc_lsn as 
    float
) as _ab_cdc_lsn,
    cast(_ab_cdc_updated_at as 
    float
) as _ab_cdc_updated_at,
    cast(_ab_cdc_deleted_at as 
    float
) as _ab_cdc_deleted_at,
    _airbyte_emitted_at
from __dbt__CTE__dedup_cdc_excluded_ab1
-- dedup_cdc_excluded
),  __dbt__CTE__dedup_cdc_excluded_ab3 as (

-- SQL model to build a hash column based on the values of this record
select
    md5(cast(
    
    coalesce(cast(id as varchar), '') || '-' || coalesce(cast(name as varchar), '') || '-' || coalesce(cast(_ab_cdc_lsn as varchar), '') || '-' || coalesce(cast(_ab_cdc_updated_at as varchar), '') || '-' || coalesce(cast(_ab_cdc_deleted_at as varchar), '')

 as varchar)) as _airbyte_dedup_cdc_excluded_hashid,
    tmp.*
from __dbt__CTE__dedup_cdc_excluded_ab2 tmp
-- dedup_cdc_excluded
),  __dbt__CTE__dedup_cdc_excluded_ab4 as (

-- SQL model to prepare for deduplicating records based on the hash record column
select
  row_number() over (
    partition by _airbyte_dedup_cdc_excluded_hashid
    order by _airbyte_emitted_at asc
  ) as _airbyte_row_num,
  tmp.*
from __dbt__CTE__dedup_cdc_excluded_ab3 tmp
-- dedup_cdc_excluded from "integrationtests".test_normalization._airbyte_raw_dedup_cdc_excluded
)-- SQL model to build a Type 2 Slowly Changing Dimension (SCD) table for each record identified by their primary key
select
    id,
    name,
    _ab_cdc_lsn,
    _ab_cdc_updated_at,
    _ab_cdc_deleted_at,
  _airbyte_emitted_at as _airbyte_start_at,
  lag(_airbyte_emitted_at) over (
    partition by id
    order by _airbyte_emitted_at is null asc, _airbyte_emitted_at desc, _airbyte_emitted_at desc
  ) as _airbyte_end_at,
  case when lag(_airbyte_emitted_at) over (
    partition by id
    order by _airbyte_emitted_at is null asc, _airbyte_emitted_at desc, _airbyte_emitted_at desc, _ab_cdc_updated_at desc
  ) is null and _ab_cdc_deleted_at is null  then 1 else 0 end as _airbyte_active_row,
  _airbyte_emitted_at,
  _airbyte_dedup_cdc_excluded_hashid
from __dbt__CTE__dedup_cdc_excluded_ab4
-- dedup_cdc_excluded from "integrationtests".test_normalization._airbyte_raw_dedup_cdc_excluded
where _airbyte_row_num = 1
  );