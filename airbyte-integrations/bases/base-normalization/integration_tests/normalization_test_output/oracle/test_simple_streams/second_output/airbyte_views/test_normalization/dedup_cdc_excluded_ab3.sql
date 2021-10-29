
  create view test_normalization.dedup_cdc_excluded_ab3__dbt_tmp as
    
with dbt__cte__dedup_cdc_excluded_ab1__ as (

-- SQL model to parse JSON blob stored in a single column and extract into separated field columns as described by the JSON Schema
select
    json_value("_AIRBYTE_DATA", '$."id"') as id,
    json_value("_AIRBYTE_DATA", '$."name"') as name,
    json_value("_AIRBYTE_DATA", '$."_ab_cdc_lsn"') as "_AB_CDC_LSN",
    json_value("_AIRBYTE_DATA", '$."_ab_cdc_updated_at"') as "_AB_CDC_UPDATED_AT",
    json_value("_AIRBYTE_DATA", '$."_ab_cdc_deleted_at"') as "_AB_CDC_DELETED_AT",
    "_AIRBYTE_AB_ID",
    "_AIRBYTE_EMITTED_AT",
    
    CURRENT_TIMESTAMP
 as "_AIRBYTE_NORMALIZED_AT"
from test_normalization.airbyte_raw_dedup_cdc_excluded 
-- dedup_cdc_excluded
where 1 = 1

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
    "_AIRBYTE_AB_ID",
    "_AIRBYTE_EMITTED_AT",
    
    CURRENT_TIMESTAMP
 as "_AIRBYTE_NORMALIZED_AT"
from dbt__cte__dedup_cdc_excluded_ab1__
-- dedup_cdc_excluded
where 1 = 1

)-- SQL model to build a hash column based on the values of this record
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
where 1 = 1


