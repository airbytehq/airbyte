

  create  table
    "integrationtests".test_normalization."nested_stream_with_complex_columns_resulting_into_long_names_scd__dbt_tmp"
    
    
  as (
    
with __dbt__CTE__nested_stream_with_complex_columns_resulting_into_long_names_ab1 as (

-- SQL model to parse JSON blob stored in a single column and extract into separated field columns as described by the JSON Schema
select
    case when json_extract_path_text(_airbyte_data, 'id', true) != '' then json_extract_path_text(_airbyte_data, 'id', true) end as id,
    case when json_extract_path_text(_airbyte_data, 'date', true) != '' then json_extract_path_text(_airbyte_data, 'date', true) end as date,
    case when json_extract_path_text(table_alias._airbyte_data, 'partition', true) != '' then json_extract_path_text(table_alias._airbyte_data, 'partition', true) end as "partition",
    _airbyte_emitted_at
from "integrationtests".test_normalization._airbyte_raw_nested_stream_with_complex_columns_resulting_into_long_names as table_alias
-- nested_stream_with_complex_columns_resulting_into_long_names
),  __dbt__CTE__nested_stream_with_complex_columns_resulting_into_long_names_ab2 as (

-- SQL model to cast each column to its adequate SQL type converted from the JSON schema type
select
    cast(id as varchar) as id,
    cast(date as varchar) as date,
    cast("partition" as varchar) as "partition",
    _airbyte_emitted_at
from __dbt__CTE__nested_stream_with_complex_columns_resulting_into_long_names_ab1
-- nested_stream_with_complex_columns_resulting_into_long_names
),  __dbt__CTE__nested_stream_with_complex_columns_resulting_into_long_names_ab3 as (

-- SQL model to build a hash column based on the values of this record
select
    *,
    md5(cast(
    
    coalesce(cast(id as varchar), '') || '-' || coalesce(cast(date as varchar), '') || '-' || coalesce(cast("partition" as varchar), '')

 as varchar)) as _airbyte_nested_stream_with_complex_columns_resulting_into_long_names_hashid
from __dbt__CTE__nested_stream_with_complex_columns_resulting_into_long_names_ab2
-- nested_stream_with_complex_columns_resulting_into_long_names
),  __dbt__CTE__nested_stream_with_complex_columns_resulting_into_long_names_ab4 as (

-- SQL model to prepare for deduplicating records based on the hash record column
select
  *,
  row_number() over (
    partition by _airbyte_nested_stream_with_complex_columns_resulting_into_long_names_hashid
    order by _airbyte_emitted_at asc
  ) as _airbyte_row_num
from __dbt__CTE__nested_stream_with_complex_columns_resulting_into_long_names_ab3
-- nested_stream_with_complex_columns_resulting_into_long_names from "integrationtests".test_normalization._airbyte_raw_nested_stream_with_complex_columns_resulting_into_long_names
)-- SQL model to build a Type 2 Slowly Changing Dimension (SCD) table for each record identified by their primary key
select
    id,
    date,
    "partition",
    date as _airbyte_start_at,
    lag(date) over (
        partition by id
        order by date is null asc, date desc, _airbyte_emitted_at desc
    ) as _airbyte_end_at,
    lag(date) over (
        partition by id
        order by date is null asc, date desc, _airbyte_emitted_at desc
    ) is null as _airbyte_active_row,
    _airbyte_emitted_at,
    _airbyte_nested_stream_with_complex_columns_resulting_into_long_names_hashid
from __dbt__CTE__nested_stream_with_complex_columns_resulting_into_long_names_ab4
-- nested_stream_with_complex_columns_resulting_into_long_names from "integrationtests".test_normalization._airbyte_raw_nested_stream_with_complex_columns_resulting_into_long_names
where _airbyte_row_num = 1
  );