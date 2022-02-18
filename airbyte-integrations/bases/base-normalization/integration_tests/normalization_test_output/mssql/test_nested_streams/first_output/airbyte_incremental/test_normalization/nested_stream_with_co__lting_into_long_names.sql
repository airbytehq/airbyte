
      
   
  USE [test_normalization];
  if object_id ('test_normalization."nested_stream_with_co__lting_into_long_names_temp_view"','V') is not null
      begin
      drop view test_normalization."nested_stream_with_co__lting_into_long_names_temp_view"
      end


   
   
  USE [test_normalization];
  if object_id ('test_normalization."nested_stream_with_co__lting_into_long_names"','U') is not null
      begin
      drop table test_normalization."nested_stream_with_co__lting_into_long_names"
      end


   USE [test_normalization];
   EXEC('create view test_normalization."nested_stream_with_co__lting_into_long_names_temp_view" as
    
-- Final base SQL model
-- depends_on: "test_normalization".test_normalization."nested_stream_with_co__lting_into_long_names_scd"
select
    _airbyte_unique_key,
    id,
    "date",
    "partition",
    _airbyte_ab_id,
    _airbyte_emitted_at,
    SYSDATETIME() as _airbyte_normalized_at,
    _airbyte_nested_strea__nto_long_names_hashid
from "test_normalization".test_normalization."nested_stream_with_co__lting_into_long_names_scd"
-- nested_stream_with_co__lting_into_long_names from "test_normalization".test_normalization._airbyte_raw_nested_stream_with_complex_columns_resulting_into_long_names
where 1 = 1
and _airbyte_active_row = 1

    ');

   SELECT * INTO "test_normalization".test_normalization."nested_stream_with_co__lting_into_long_names" FROM
    "test_normalization".test_normalization."nested_stream_with_co__lting_into_long_names_temp_view"

   
   
  USE [test_normalization];
  if object_id ('test_normalization."nested_stream_with_co__lting_into_long_names_temp_view"','V') is not null
      begin
      drop view test_normalization."nested_stream_with_co__lting_into_long_names_temp_view"
      end

    
   use [test_normalization];
  if EXISTS (
        SELECT * FROM
        sys.indexes WHERE name = 'test_normalization_nested_stream_with_co__lting_into_long_names_cci'
        AND object_id=object_id('test_normalization_nested_stream_with_co__lting_into_long_names')
    )
  DROP index test_normalization.nested_stream_with_co__lting_into_long_names.test_normalization_nested_stream_with_co__lting_into_long_names_cci
  CREATE CLUSTERED COLUMNSTORE INDEX test_normalization_nested_stream_with_co__lting_into_long_names_cci
    ON test_normalization.nested_stream_with_co__lting_into_long_names

   


  