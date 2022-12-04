
      

  create  table "postgres"._airbyte_test_normalization."renamed_dedup_cdc_excluded_stg"
  as (
    
with __dbt__cte__renamed_dedup_cdc_excluded_ab1 as (

-- SQL model to parse JSON blob stored in a single column and extract into separated field columns as described by the JSON Schema
-- depends_on: "postgres".test_normalization._airbyte_raw_renamed_dedup_cdc_excluded
select
    jsonb_extract_path_text(_airbyte_data, 'id') as "id",
    jsonb_extract_path_text(_airbyte_data, '_ab_cdc_updated_at') as _ab_cdc_updated_at,
    _airbyte_ab_id,
    _airbyte_emitted_at,
    now() as _airbyte_normalized_at
from "postgres".test_normalization._airbyte_raw_renamed_dedup_cdc_excluded as table_alias
-- renamed_dedup_cdc_excluded
where 1 = 1

),  __dbt__cte__renamed_dedup_cdc_excluded_ab2 as (

-- SQL model to cast each column to its adequate SQL type converted from the JSON schema type
-- depends_on: __dbt__cte__renamed_dedup_cdc_excluded_ab1
select
    cast("id" as 
    bigint
) as "id",
    cast(_ab_cdc_updated_at as 
    float
) as _ab_cdc_updated_at,
    _airbyte_ab_id,
    _airbyte_emitted_at,
    now() as _airbyte_normalized_at
from __dbt__cte__renamed_dedup_cdc_excluded_ab1
-- renamed_dedup_cdc_excluded
where 1 = 1

)-- SQL model to build a hash column based on the values of this record
-- depends_on: __dbt__cte__renamed_dedup_cdc_excluded_ab2
select
    md5(cast(coalesce(cast("id" as text), '') || '-' || coalesce(cast(_ab_cdc_updated_at as text), '') as text)) as _airbyte_renamed_dedup_cdc_excluded_hashid,
    tmp.*
from __dbt__cte__renamed_dedup_cdc_excluded_ab2 tmp
-- renamed_dedup_cdc_excluded
where 1 = 1

  );
  