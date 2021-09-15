

  create  table test_normalization.nested_stream_with_complex_columns_resulting_into_long_names_scd__dbt_tmp
  
  as
    
with dbt__cte__nested_stream_with_complex_columns_resulting_into_long_names_ab1__ as (

-- SQL model to parse JSON blob stored in a single column and extract into separated field columns as described by the JSON Schema
select
    json_value("_AIRBYTE_DATA", '$."id"') as id,
    json_value("_AIRBYTE_DATA", '$."date"') as "DATE",
    json_value("_AIRBYTE_DATA", '$."partition"') as partition,
    "_AIRBYTE_EMITTED_AT"
from test_normalization.airbyte_raw_nested_stream_with_complex_columns_resulting_into_long_names 
-- nested_stream_with_complex_columns_resulting_into_long_names
),  dbt__cte__nested_stream_with_complex_columns_resulting_into_long_names_ab2__ as (

-- SQL model to cast each column to its adequate SQL type converted from the JSON schema type
select
    cast(id as varchar2(4000)) as id,
    cast("DATE" as varchar2(4000)) as "DATE",
    cast(partition as varchar2(4000)) as partition,
    "_AIRBYTE_EMITTED_AT"
from dbt__cte__nested_stream_with_complex_columns_resulting_into_long_names_ab1__
-- nested_stream_with_complex_columns_resulting_into_long_names
),  dbt__cte__nested_stream_with_complex_columns_resulting_into_long_names_ab3__ as (

-- SQL model to build a hash column based on the values of this record
select
    ora_hash(
            
                id || '~' ||
            
            
                "DATE" || '~' ||
            
            
                partition
            
    ) as "_AIRBYTE_NESTED_STREAM_WITH_COMPLEX_COLUMNS_RESULTING_INTO_LONG_NAMES_HASHID",
    tmp.*
from dbt__cte__nested_stream_with_complex_columns_resulting_into_long_names_ab2__ tmp
-- nested_stream_with_complex_columns_resulting_into_long_names
),  dbt__cte__nested_stream_with_complex_columns_resulting_into_long_names_ab4__ as (

-- SQL model to prepare for deduplicating records based on the hash record column
select
  row_number() over (
    partition by "_AIRBYTE_NESTED_STREAM_WITH_COMPLEX_COLUMNS_RESULTING_INTO_LONG_NAMES_HASHID"
    order by "_AIRBYTE_EMITTED_AT" asc
  ) as "_AIRBYTE_ROW_NUM",
  tmp.*
from dbt__cte__nested_stream_with_complex_columns_resulting_into_long_names_ab3__ tmp
-- nested_stream_with_complex_columns_resulting_into_long_names from test_normalization.airbyte_raw_nested_stream_with_complex_columns_resulting_into_long_names
)-- SQL model to build a Type 2 Slowly Changing Dimension (SCD) table for each record identified by their primary key
select
    id,
    "DATE",
    partition,
  "DATE" as "_AIRBYTE_START_AT",
  lag("DATE") over (
    partition by id
    order by "DATE" asc nulls first, "DATE" desc, "_AIRBYTE_EMITTED_AT" desc
  ) as "_AIRBYTE_END_AT",
  case when lag("DATE") over (
    partition by id
    order by "DATE" asc nulls first, "DATE" desc, "_AIRBYTE_EMITTED_AT" desc
  ) is null  then 1 else 0 end as "_AIRBYTE_ACTIVE_ROW",
  "_AIRBYTE_EMITTED_AT",
  "_AIRBYTE_NESTED_STREAM_WITH_COMPLEX_COLUMNS_RESULTING_INTO_LONG_NAMES_HASHID"
from dbt__cte__nested_stream_with_complex_columns_resulting_into_long_names_ab4__
-- nested_stream_with_complex_columns_resulting_into_long_names from test_normalization.airbyte_raw_nested_stream_with_complex_columns_resulting_into_long_names
where "_AIRBYTE_ROW_NUM" = 1