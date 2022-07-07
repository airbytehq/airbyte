
      

  create  table "postgres"._airbyte_test_normalization."some_stream_that_was_empty_stg"
  as (
    
with __dbt__cte__some_stream_that_was_empty_ab1 as (

-- SQL model to parse JSON blob stored in a single column and extract into separated field columns as described by the JSON Schema
-- depends_on: "postgres".test_normalization._airbyte_raw_some_stream_that_was_empty
select
    jsonb_extract_path_text(_airbyte_data, 'id') as "id",
    jsonb_extract_path_text(_airbyte_data, 'date') as "date",
    _airbyte_ab_id,
    _airbyte_emitted_at,
    now() as _airbyte_normalized_at
from "postgres".test_normalization._airbyte_raw_some_stream_that_was_empty as table_alias
-- some_stream_that_was_empty
where 1 = 1

),  __dbt__cte__some_stream_that_was_empty_ab2 as (

-- SQL model to cast each column to its adequate SQL type converted from the JSON schema type
-- depends_on: __dbt__cte__some_stream_that_was_empty_ab1
select
    cast("id" as text) as "id",
    cast("date" as text) as "date",
    _airbyte_ab_id,
    _airbyte_emitted_at,
    now() as _airbyte_normalized_at
from __dbt__cte__some_stream_that_was_empty_ab1
-- some_stream_that_was_empty
where 1 = 1

)-- SQL model to build a hash column based on the values of this record
-- depends_on: __dbt__cte__some_stream_that_was_empty_ab2
select
    md5(cast(coalesce(cast("id" as text), '') || '-' || coalesce(cast("date" as text), '') as text)) as _airbyte_some_stream_that_was_empty_hashid,
    tmp.*
from __dbt__cte__some_stream_that_was_empty_ab2 tmp
-- some_stream_that_was_empty
where 1 = 1

  );
  