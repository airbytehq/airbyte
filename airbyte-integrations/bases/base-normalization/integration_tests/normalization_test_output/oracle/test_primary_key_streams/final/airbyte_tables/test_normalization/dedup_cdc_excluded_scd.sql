

  create  table test_normalization.dedup_cdc_excluded_scd__dbt_tmp
  
  as
    
with dbt__cte__dedup_cdc_excluded_ab1__ as (

-- SQL model to parse JSON blob stored in a single column and extract into separated field columns as described by the JSON Schema
select
    json_value(airbyte_data, '$."id"') as id,
    json_value(airbyte_data, '$."name"') as name,
    json_value(airbyte_data, '$."_ab_cdc_lsn"') as "_AB_CDC_LSN",
    json_value(airbyte_data, '$."_ab_cdc_updated_at"') as "_AB_CDC_UPDATED_AT",
    json_value(airbyte_data, '$."_ab_cdc_deleted_at"') as "_AB_CDC_DELETED_AT",
    airbyte_emitted_at
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
    airbyte_emitted_at
from dbt__cte__dedup_cdc_excluded_ab1__
-- dedup_cdc_excluded
),  dbt__cte__dedup_cdc_excluded_ab3__ as (

-- SQL model to build a hash column based on the values of this record
select
    ora_hash(
        'id' || '~' ||
        'name' || '~' ||
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
    order by airbyte_emitted_at asc
  ) as airbyte_row_num,
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
    airbyte_emitted_at as airbyte_start_at,
    lag(airbyte_emitted_at) over (
        partition by id
        order by airbyte_emitted_at desc, airbyte_emitted_at desc
    ) as airbyte_end_at,
    coalesce(cast(lag(airbyte_emitted_at) over (
        partition by id
        order by airbyte_emitted_at desc, airbyte_emitted_at desc
    ) as varchar(200)), 'Latest') as airbyte_active_row,
    airbyte_emitted_at,
    "_AIRBYTE_DEDUP_CDC_EXCLUDED_HASHID"
from dbt__cte__dedup_cdc_excluded_ab4__
-- dedup_cdc_excluded from test_normalization.airbyte_raw_dedup_cdc_excluded
where airbyte_row_num = 1