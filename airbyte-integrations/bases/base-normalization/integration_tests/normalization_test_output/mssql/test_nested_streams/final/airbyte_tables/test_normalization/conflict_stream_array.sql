
   
  USE [test_normalization];
  if object_id ('test_normalization."conflict_stream_array__dbt_tmp_temp_view"','V') is not null
      begin
      drop view test_normalization."conflict_stream_array__dbt_tmp_temp_view"
      end


   
   
  USE [test_normalization];
  if object_id ('test_normalization."conflict_stream_array__dbt_tmp"','U') is not null
      begin
      drop table test_normalization."conflict_stream_array__dbt_tmp"
      end


   USE [test_normalization];
   EXEC('create view test_normalization."conflict_stream_array__dbt_tmp_temp_view" as
    
-- Final base SQL model
select
    id,
    conflict_stream_array,
    _airbyte_emitted_at,
    _airbyte_conflict_stream_array_hashid
from "test_normalization"._airbyte_test_normalization."conflict_stream_array_ab3"
-- conflict_stream_array from "test_normalization".test_normalization._airbyte_raw_conflict_stream_array
    ');

   SELECT * INTO "test_normalization".test_normalization."conflict_stream_array__dbt_tmp" FROM
    "test_normalization".test_normalization."conflict_stream_array__dbt_tmp_temp_view"

   
   
  USE [test_normalization];
  if object_id ('test_normalization."conflict_stream_array__dbt_tmp_temp_view"','V') is not null
      begin
      drop view test_normalization."conflict_stream_array__dbt_tmp_temp_view"
      end

    
   use [test_normalization];
  if EXISTS (
        SELECT * FROM
        sys.indexes WHERE name = 'test_normalization_conflict_stream_array__dbt_tmp_cci'
        AND object_id=object_id('test_normalization_conflict_stream_array__dbt_tmp')
    )
  DROP index test_normalization.conflict_stream_array__dbt_tmp.test_normalization_conflict_stream_array__dbt_tmp_cci
  CREATE CLUSTERED COLUMNSTORE INDEX test_normalization_conflict_stream_array__dbt_tmp_cci
    ON test_normalization.conflict_stream_array__dbt_tmp

   

