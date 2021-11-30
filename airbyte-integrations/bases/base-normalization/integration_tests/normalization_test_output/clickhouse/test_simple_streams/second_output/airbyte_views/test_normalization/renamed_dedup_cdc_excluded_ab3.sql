

  create view _airbyte_test_normalization.renamed_dedup_cdc_excluded_ab3__dbt_tmp 
  
  as (
    
with __dbt__cte__renamed_dedup_cdc_excluded_ab1 as (

-- SQL model to parse JSON blob stored in a single column and extract into separated field columns as described by the JSON Schema
select
    JSONExtractRaw(_airbyte_data, 'id') as id,
    _airbyte_ab_id,
    _airbyte_emitted_at,
    now() as _airbyte_normalized_at
from test_normalization._airbyte_raw_renamed_dedup_cdc_excluded as table_alias
-- renamed_dedup_cdc_excluded
where 1 = 1

),  __dbt__cte__renamed_dedup_cdc_excluded_ab2 as (

-- SQL model to cast each column to its adequate SQL type converted from the JSON schema type
select
    accurateCastOrNull(id, '
    BIGINT
') as id,
    _airbyte_ab_id,
    _airbyte_emitted_at,
    now() as _airbyte_normalized_at
from __dbt__cte__renamed_dedup_cdc_excluded_ab1
-- renamed_dedup_cdc_excluded
where 1 = 1

)-- SQL model to build a hash column based on the values of this record
select
    assumeNotNull(hex(MD5(
            
                toString(id)
            
    ))) as _airbyte_renamed_dedup_cdc_excluded_hashid,
    tmp.*
from __dbt__cte__renamed_dedup_cdc_excluded_ab2 tmp
-- renamed_dedup_cdc_excluded
where 1 = 1

  )