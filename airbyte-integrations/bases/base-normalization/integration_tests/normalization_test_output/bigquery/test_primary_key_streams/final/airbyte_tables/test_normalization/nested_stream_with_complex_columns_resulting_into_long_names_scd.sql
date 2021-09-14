

  create or replace table `dataline-integration-testing`.test_normalization.`nested_stream_with_complex_columns_resulting_into_long_names_scd`
  
  
  OPTIONS()
  as (
    
with __dbt__CTE__nested_stream_with_complex_columns_resulting_into_long_names_ab1 as (

-- SQL model to parse JSON blob stored in a single column and extract into separated field columns as described by the JSON Schema
select
    json_extract_scalar(_airbyte_data, "$['id']") as id,
    json_extract_scalar(_airbyte_data, "$['date']") as date,
    
        json_extract(table_alias._airbyte_data, "$['partition']")
     as `partition`,
    _airbyte_emitted_at
from `dataline-integration-testing`.test_normalization._airbyte_raw_nested_stream_with_complex_columns_resulting_into_long_names as table_alias
-- nested_stream_with_complex_columns_resulting_into_long_names
),  __dbt__CTE__nested_stream_with_complex_columns_resulting_into_long_names_ab2 as (

-- SQL model to cast each column to its adequate SQL type converted from the JSON schema type
select
    cast(id as 
    string
) as id,
    cast(date as 
    string
) as date,
    cast(`partition` as 
    string
) as `partition`,
    _airbyte_emitted_at
from __dbt__CTE__nested_stream_with_complex_columns_resulting_into_long_names_ab1
-- nested_stream_with_complex_columns_resulting_into_long_names
),  __dbt__CTE__nested_stream_with_complex_columns_resulting_into_long_names_ab3 as (

-- SQL model to build a hash column based on the values of this record
select
    to_hex(md5(cast(concat(coalesce(cast(id as 
    string
), ''), '-', coalesce(cast(date as 
    string
), ''), '-', coalesce(cast(`partition` as 
    string
), '')) as 
    string
))) as _airbyte_nested_stream_with_complex_columns_resulting_into_long_names_hashid,
    tmp.*
from __dbt__CTE__nested_stream_with_complex_columns_resulting_into_long_names_ab2 tmp
-- nested_stream_with_complex_columns_resulting_into_long_names
),  __dbt__CTE__nested_stream_with_complex_columns_resulting_into_long_names_ab4 as (

-- SQL model to prepare for deduplicating records based on the hash record column
select
  row_number() over (
    partition by _airbyte_nested_stream_with_complex_columns_resulting_into_long_names_hashid
    order by _airbyte_emitted_at asc
  ) as _airbyte_row_num,
  tmp.*
from __dbt__CTE__nested_stream_with_complex_columns_resulting_into_long_names_ab3 tmp
-- nested_stream_with_complex_columns_resulting_into_long_names from `dataline-integration-testing`.test_normalization._airbyte_raw_nested_stream_with_complex_columns_resulting_into_long_names
)-- SQL model to build a Type 2 Slowly Changing Dimension (SCD) table for each record identified by their primary key
select
    id,
    date,
    `partition`,
  date as _airbyte_start_at,
  lag(date) over (
    partition by id
    order by date is null asc, date desc, _airbyte_emitted_at desc
  ) as _airbyte_end_at,
  case when lag(date) over (
    partition by id
    order by date is null asc, date desc, _airbyte_emitted_at desc
  ) is null  then 1 else 0 end as _airbyte_active_row,
  _airbyte_emitted_at,
  _airbyte_nested_stream_with_complex_columns_resulting_into_long_names_hashid
from __dbt__CTE__nested_stream_with_complex_columns_resulting_into_long_names_ab4
-- nested_stream_with_complex_columns_resulting_into_long_names from `dataline-integration-testing`.test_normalization._airbyte_raw_nested_stream_with_complex_columns_resulting_into_long_names
where _airbyte_row_num = 1
  );
    