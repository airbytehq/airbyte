
      

  create  table "postgres"._airbyte_test_normalization."nested_stream_with_c__lting_into_long_names_stg"
  as (
    
with __dbt__cte__nested_stream_with_c__lting_into_long_names_ab1 as (

-- SQL model to parse JSON blob stored in a single column and extract into separated field columns as described by the JSON Schema
-- depends_on: "postgres".test_normalization._airbyte_raw_nested_stream_with_complex_columns_resulting_into_long_names
select
    jsonb_extract_path_text(_airbyte_data, 'id') as "id",
    jsonb_extract_path_text(_airbyte_data, 'date') as "date",
    
        jsonb_extract_path(table_alias._airbyte_data, 'partition')
     as "partition",
    _airbyte_ab_id,
    _airbyte_emitted_at,
    now() as _airbyte_normalized_at
from "postgres".test_normalization._airbyte_raw_nested_stream_with_complex_columns_resulting_into_long_names as table_alias
-- nested_stream_with_c__lting_into_long_names
where 1 = 1

),  __dbt__cte__nested_stream_with_c__lting_into_long_names_ab2 as (

-- SQL model to cast each column to its adequate SQL type converted from the JSON schema type
-- depends_on: __dbt__cte__nested_stream_with_c__lting_into_long_names_ab1
select
    cast("id" as text) as "id",
    cast("date" as text) as "date",
    cast("partition" as 
    jsonb
) as "partition",
    _airbyte_ab_id,
    _airbyte_emitted_at,
    now() as _airbyte_normalized_at
from __dbt__cte__nested_stream_with_c__lting_into_long_names_ab1
-- nested_stream_with_c__lting_into_long_names
where 1 = 1

)-- SQL model to build a hash column based on the values of this record
-- depends_on: __dbt__cte__nested_stream_with_c__lting_into_long_names_ab2
select
    md5(cast(coalesce(cast("id" as text), '') || '-' || coalesce(cast("date" as text), '') || '-' || coalesce(cast("partition" as text), '') as text)) as _airbyte_nested_stre__nto_long_names_hashid,
    tmp.*
from __dbt__cte__nested_stream_with_c__lting_into_long_names_ab2 tmp
-- nested_stream_with_c__lting_into_long_names
where 1 = 1

  );
  