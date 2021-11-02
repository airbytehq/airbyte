
  create view test_normalization.renamed_dedup_cdc_excluded_ab3__dbt_tmp as
    
with dbt__cte__renamed_dedup_cdc_excluded_ab1__ as (

-- SQL model to parse JSON blob stored in a single column and extract into separated field columns as described by the JSON Schema
select
    json_value("_AIRBYTE_DATA", '$."id"') as id,
    "_AIRBYTE_AB_ID",
    "_AIRBYTE_EMITTED_AT",
    
    CURRENT_TIMESTAMP
 as "_AIRBYTE_NORMALIZED_AT"
from test_normalization.airbyte_raw_renamed_dedup_cdc_excluded 
-- renamed_dedup_cdc_excluded
where 1 = 1

),  dbt__cte__renamed_dedup_cdc_excluded_ab2__ as (

-- SQL model to cast each column to its adequate SQL type converted from the JSON schema type
select
    cast(id as 
    numeric
) as id,
    "_AIRBYTE_AB_ID",
    "_AIRBYTE_EMITTED_AT",
    
    CURRENT_TIMESTAMP
 as "_AIRBYTE_NORMALIZED_AT"
from dbt__cte__renamed_dedup_cdc_excluded_ab1__
-- renamed_dedup_cdc_excluded
where 1 = 1

)-- SQL model to build a hash column based on the values of this record
select
    ora_hash(
            
                id
            
    ) as "_AIRBYTE_RENAMED_DEDUP_CDC_EXCLUDED_HASHID",
    tmp.*
from dbt__cte__renamed_dedup_cdc_excluded_ab2__ tmp
-- renamed_dedup_cdc_excluded
where 1 = 1


