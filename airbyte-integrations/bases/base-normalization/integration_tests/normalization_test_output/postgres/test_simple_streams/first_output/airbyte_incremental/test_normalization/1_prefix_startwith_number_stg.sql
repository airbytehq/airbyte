
      

  create  table "postgres"._airbyte_test_normalization."1_prefix_startwith_number_stg"
  as (
    
with __dbt__cte__1_prefix_startwith_number_ab1 as (

-- SQL model to parse JSON blob stored in a single column and extract into separated field columns as described by the JSON Schema
-- depends_on: "postgres".test_normalization._airbyte_raw_1_prefix_startwith_number
select
    jsonb_extract_path_text(_airbyte_data, 'id') as "id",
    jsonb_extract_path_text(_airbyte_data, 'date') as "date",
    jsonb_extract_path_text(_airbyte_data, 'text') as "text",
    _airbyte_ab_id,
    _airbyte_emitted_at,
    now() as _airbyte_normalized_at
from "postgres".test_normalization._airbyte_raw_1_prefix_startwith_number as table_alias
-- 1_prefix_startwith_number
where 1 = 1

),  __dbt__cte__1_prefix_startwith_number_ab2 as (

-- SQL model to cast each column to its adequate SQL type converted from the JSON schema type
-- depends_on: __dbt__cte__1_prefix_startwith_number_ab1
select
    cast("id" as 
    bigint
) as "id",
    cast(nullif("date", '') as 
    date
) as "date",
    cast("text" as text) as "text",
    _airbyte_ab_id,
    _airbyte_emitted_at,
    now() as _airbyte_normalized_at
from __dbt__cte__1_prefix_startwith_number_ab1
-- 1_prefix_startwith_number
where 1 = 1

)-- SQL model to build a hash column based on the values of this record
-- depends_on: __dbt__cte__1_prefix_startwith_number_ab2
select
    md5(cast(coalesce(cast("id" as text), '') || '-' || coalesce(cast("date" as text), '') || '-' || coalesce(cast("text" as text), '') as text)) as _airbyte_1_prefix_startwith_number_hashid,
    tmp.*
from __dbt__cte__1_prefix_startwith_number_ab2 tmp
-- 1_prefix_startwith_number
where 1 = 1

  );
  