
   
  USE [test_normalization];
  if object_id ('test_normalization."nested_stream_with_co__lting_into_long_names_scd__dbt_tmp_temp_view"','V') is not null
      begin
      drop view test_normalization."nested_stream_with_co__lting_into_long_names_scd__dbt_tmp_temp_view"
      end


   
   
  USE [test_normalization];
  if object_id ('test_normalization."nested_stream_with_co__lting_into_long_names_scd__dbt_tmp"','U') is not null
      begin
      drop table test_normalization."nested_stream_with_co__lting_into_long_names_scd__dbt_tmp"
      end


   USE [test_normalization];
   EXEC('create view test_normalization."nested_stream_with_co__lting_into_long_names_scd__dbt_tmp_temp_view" as
    
with __dbt__CTE__nested_stream_with_co__lting_into_long_names_ab1 as (

-- SQL model to parse JSON blob stored in a single column and extract into separated field columns as described by the JSON Schema
select
    json_value(_airbyte_data, ''$."id"'') as id,
    json_value(_airbyte_data, ''$."date"'') as "date",
    json_query(_airbyte_data, ''$."partition"'') as "partition",
    _airbyte_emitted_at
from "test_normalization".test_normalization._airbyte_raw_nested_stream_with_complex_columns_resulting_into_long_names as table_alias
-- nested_stream_with_co__lting_into_long_names
),  __dbt__CTE__nested_stream_with_co__lting_into_long_names_ab2 as (

-- SQL model to cast each column to its adequate SQL type converted from the JSON schema type
select
    cast(id as 
    VARCHAR(max)) as id,
    cast("date" as 
    VARCHAR(max)) as "date",
    cast("partition" as VARCHAR(max)) as "partition",
    _airbyte_emitted_at
from __dbt__CTE__nested_stream_with_co__lting_into_long_names_ab1
-- nested_stream_with_co__lting_into_long_names
),  __dbt__CTE__nested_stream_with_co__lting_into_long_names_ab3 as (

-- SQL model to build a hash column based on the values of this record
select
    convert(varchar(32), HashBytes(''md5'',  coalesce(cast(
    
    

    concat(concat(coalesce(cast(id as 
    VARCHAR(max)), ''''), ''-'', coalesce(cast("date" as 
    VARCHAR(max)), ''''), ''-'', coalesce(cast("partition" as 
    VARCHAR(max)), ''''),''''), '''') as 
    VARCHAR(max)), '''')), 2) as _airbyte_nested_strea__nto_long_names_hashid,
    tmp.*
from __dbt__CTE__nested_stream_with_co__lting_into_long_names_ab2 tmp
-- nested_stream_with_co__lting_into_long_names
),  __dbt__CTE__nested_stream_with_co__lting_into_long_names_ab4 as (

-- SQL model to prepare for deduplicating records based on the hash record column
select
  row_number() over (
    partition by _airbyte_nested_strea__nto_long_names_hashid
    order by _airbyte_emitted_at asc
  ) as _airbyte_row_num,
  tmp.*
from __dbt__CTE__nested_stream_with_co__lting_into_long_names_ab3 tmp
-- nested_stream_with_co__lting_into_long_names from "test_normalization".test_normalization._airbyte_raw_nested_stream_with_complex_columns_resulting_into_long_names
)-- SQL model to build a Type 2 Slowly Changing Dimension (SCD) table for each record identified by their primary key
select
    id,
    "date",
    "partition",
  "date" as _airbyte_start_at,
  lag("date") over (
    partition by id
    order by "date" desc, "date" desc, _airbyte_emitted_at desc
  ) as _airbyte_end_at,
  case when lag("date") over (
    partition by id
    order by "date" desc, "date" desc, _airbyte_emitted_at desc
  ) is null  then 1 else 0 end as _airbyte_active_row,
  _airbyte_emitted_at,
  _airbyte_nested_strea__nto_long_names_hashid
from __dbt__CTE__nested_stream_with_co__lting_into_long_names_ab4
-- nested_stream_with_co__lting_into_long_names from "test_normalization".test_normalization._airbyte_raw_nested_stream_with_complex_columns_resulting_into_long_names
where _airbyte_row_num = 1
    ');

   SELECT * INTO "test_normalization".test_normalization."nested_stream_with_co__lting_into_long_names_scd__dbt_tmp" FROM
    "test_normalization".test_normalization."nested_stream_with_co__lting_into_long_names_scd__dbt_tmp_temp_view"

   
   
  USE [test_normalization];
  if object_id ('test_normalization."nested_stream_with_co__lting_into_long_names_scd__dbt_tmp_temp_view"','V') is not null
      begin
      drop view test_normalization."nested_stream_with_co__lting_into_long_names_scd__dbt_tmp_temp_view"
      end

    
   use [test_normalization];
  if EXISTS (
        SELECT * FROM
        sys.indexes WHERE name = 'test_normalization_nested_stream_with_co__lting_into_long_names_scd__dbt_tmp_cci'
        AND object_id=object_id('test_normalization_nested_stream_with_co__lting_into_long_names_scd__dbt_tmp')
    )
  DROP index test_normalization.nested_stream_with_co__lting_into_long_names_scd__dbt_tmp.test_normalization_nested_stream_with_co__lting_into_long_names_scd__dbt_tmp_cci
  CREATE CLUSTERED COLUMNSTORE INDEX test_normalization_nested_stream_with_co__lting_into_long_names_scd__dbt_tmp_cci
    ON test_normalization.nested_stream_with_co__lting_into_long_names_scd__dbt_tmp

   

