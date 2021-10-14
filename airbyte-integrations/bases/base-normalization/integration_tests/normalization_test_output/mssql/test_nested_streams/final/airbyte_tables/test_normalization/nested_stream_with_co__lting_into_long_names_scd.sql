
   
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
    
-- SQL model to build a Type 2 Slowly Changing Dimension (SCD) table for each record identified by their primary key
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
from "test_normalization"._airbyte_test_normalization."nested_stream_with_co__lting_into_long_names_ab4"
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

   

