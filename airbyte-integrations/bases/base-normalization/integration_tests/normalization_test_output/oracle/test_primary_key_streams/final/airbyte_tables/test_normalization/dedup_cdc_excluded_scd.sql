

  create  table test_normalization.dedup_cdc_excluded_scd__dbt_tmp
  
  as
    
with dbt__cte__dedup_cdc_excluded_ab1__ as (

-- SQL model to parse JSON blob stored in a single column and extract into separated field columns as described by the JSON Schema
select
    json_value("_AIRBYTE_DATA", '$."id"') as id,
    json_value("_AIRBYTE_DATA", '$."name"') as name,
    json_value("_AIRBYTE_DATA", '$."_ab_cdc_lsn"') as "_AB_CDC_LSN",
    json_value("_AIRBYTE_DATA", '$."_ab_cdc_updated_at"') as "_AB_CDC_UPDATED_AT",
    json_value("_AIRBYTE_DATA", '$."_ab_cdc_deleted_at"') as "_AB_CDC_DELETED_AT",
    "_AIRBYTE_EMITTED_AT"
from test_normalization.airbyte_raw_dedup_cdc_excluded 
-- dedup_cdc_excluded
),  dbt__cte__dedup_cdc_excluded_ab2__ as (

-- SQL model to cast each column to its adequate SQL type converted from the JSON schema type
select
    cast(id as 
    numeric
) as id,
    cast(name as varchar2(4000)) as name,
    cast("_AB_CDC_LSN" as 
    float
) as "_AB_CDC_LSN",
    cast("_AB_CDC_UPDATED_AT" as 
    float
) as "_AB_CDC_UPDATED_AT",
    cast("_AB_CDC_DELETED_AT" as 
    float
) as "_AB_CDC_DELETED_AT",
    "_AIRBYTE_EMITTED_AT"
from dbt__cte__dedup_cdc_excluded_ab1__
-- dedup_cdc_excluded
),  dbt__cte__dedup_cdc_excluded_ab3__ as (

-- SQL model to build a hash column based on the values of this record
select
    ora_hash(
            
                id || '~' ||
            
            
                name || '~' ||
            
            
                "_AB_CDC_LSN" || '~' ||
            
            
                "_AB_CDC_UPDATED_AT" || '~' ||
            
            
                "_AB_CDC_DELETED_AT"
            
    ) as "_AIRBYTE_DEDUP_CDC_EXCLUDED_HASHID",
    tmp.*
from dbt__cte__dedup_cdc_excluded_ab2__ tmp
-- dedup_cdc_excluded
),  dbt__cte__dedup_cdc_excluded_ab4__ as (

-- SQL model to prepare for deduplicating records based on the hash record column
select
  row_number() over (
    partition by "_AIRBYTE_DEDUP_CDC_EXCLUDED_HASHID"
    order by "_AIRBYTE_EMITTED_AT" asc
  ) as "_AIRBYTE_ROW_NUM",
  tmp.*
from dbt__cte__dedup_cdc_excluded_ab3__ tmp
-- dedup_cdc_excluded from test_normalization.airbyte_raw_dedup_cdc_excluded
)-- SQL model to build a Type 2 Slowly Changing Dimension (SCD) table for each record identified by their primary key
select
    id,
    name,
    "_AB_CDC_LSN",
    "_AB_CDC_UPDATED_AT",
    "_AB_CDC_DELETED_AT",
  "_AIRBYTE_EMITTED_AT" as "_AIRBYTE_START_AT",
  lag("_AIRBYTE_EMITTED_AT") over (
    partition by id
    order by "_AIRBYTE_EMITTED_AT" asc nulls first, "_AIRBYTE_EMITTED_AT" desc, "_AIRBYTE_EMITTED_AT" desc
  ) as "_AIRBYTE_END_AT",
  case when lag("_AIRBYTE_EMITTED_AT") over (
    partition by id
    order by "_AIRBYTE_EMITTED_AT" asc nulls first, "_AIRBYTE_EMITTED_AT" desc, "_AIRBYTE_EMITTED_AT" desc, "_AB_CDC_UPDATED_AT" desc
  ) is null and "_AB_CDC_DELETED_AT" is null  then 1 else 0 end as "_AIRBYTE_ACTIVE_ROW",
  "_AIRBYTE_EMITTED_AT",
  "_AIRBYTE_DEDUP_CDC_EXCLUDED_HASHID"
from dbt__cte__dedup_cdc_excluded_ab4__
-- dedup_cdc_excluded from test_normalization.airbyte_raw_dedup_cdc_excluded
where "_AIRBYTE_ROW_NUM" = 1