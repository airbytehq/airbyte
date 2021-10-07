
   
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
    
with __dbt__CTE__conflict_stream_array_ab1 as (

-- SQL model to parse JSON blob stored in a single column and extract into separated field columns as described by the JSON Schema
select
    json_value(_airbyte_data, ''$."id"'') as id,
    json_query(_airbyte_data, ''$."conflict_stream_array"'') as conflict_stream_array,
    _airbyte_emitted_at
from "test_normalization".test_normalization._airbyte_raw_conflict_stream_array as table_alias
-- conflict_stream_array
),  __dbt__CTE__conflict_stream_array_ab2 as (

-- SQL model to cast each column to its adequate SQL type converted from the JSON schema type
select
    cast(id as 
    VARCHAR(max)) as id,
    conflict_stream_array,
    _airbyte_emitted_at
from __dbt__CTE__conflict_stream_array_ab1
-- conflict_stream_array
),  __dbt__CTE__conflict_stream_array_ab3 as (

-- SQL model to build a hash column based on the values of this record
select
    convert(varchar(32), HashBytes(''md5'',  coalesce(cast(
    
    

    concat(concat(coalesce(cast(id as 
    VARCHAR(max)), ''''), ''-'', coalesce(cast(cast(conflict_stream_array as 
    VARCHAR(max)) as 
    VARCHAR(max)), ''''),''''), '''') as 
    VARCHAR(max)), '''')), 2) as _airbyte_conflict_stream_array_hashid,
    tmp.*
from __dbt__CTE__conflict_stream_array_ab2 tmp
-- conflict_stream_array
)-- Final base SQL model
select
    id,
    conflict_stream_array,
    _airbyte_emitted_at,
    _airbyte_conflict_stream_array_hashid
from __dbt__CTE__conflict_stream_array_ab3
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

   

