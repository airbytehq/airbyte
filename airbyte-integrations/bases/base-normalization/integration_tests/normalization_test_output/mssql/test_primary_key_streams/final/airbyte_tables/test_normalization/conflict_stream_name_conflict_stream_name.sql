
   
  USE [test_normalization];
  if object_id ('test_normalization."conflict_stream_name_conflict_stream_name__dbt_tmp_temp_view"','V') is not null
      begin
      drop view test_normalization."conflict_stream_name_conflict_stream_name__dbt_tmp_temp_view"
      end


   
   
  USE [test_normalization];
  if object_id ('test_normalization."conflict_stream_name_conflict_stream_name__dbt_tmp"','U') is not null
      begin
      drop table test_normalization."conflict_stream_name_conflict_stream_name__dbt_tmp"
      end


   USE [test_normalization];
   EXEC('create view test_normalization."conflict_stream_name_conflict_stream_name__dbt_tmp_temp_view" as
    
with __dbt__CTE__conflict_stream_name_conflict_stream_name_ab1 as (

-- SQL model to parse JSON blob stored in a single column and extract into separated field columns as described by the JSON Schema
select
    _airbyte_conflict_stream_name_hashid,
    json_query(conflict_stream_name, ''$."conflict_stream_name"'') as conflict_stream_name,
    _airbyte_emitted_at
from "test_normalization".test_normalization."conflict_stream_name" as table_alias
where conflict_stream_name is not null
-- conflict_stream_name at conflict_stream_name/conflict_stream_name
),  __dbt__CTE__conflict_stream_name_conflict_stream_name_ab2 as (

-- SQL model to cast each column to its adequate SQL type converted from the JSON schema type
select
    _airbyte_conflict_stream_name_hashid,
    cast(conflict_stream_name as VARCHAR(max)) as conflict_stream_name,
    _airbyte_emitted_at
from __dbt__CTE__conflict_stream_name_conflict_stream_name_ab1
-- conflict_stream_name at conflict_stream_name/conflict_stream_name
),  __dbt__CTE__conflict_stream_name_conflict_stream_name_ab3 as (

-- SQL model to build a hash column based on the values of this record
select
    convert(varchar(32), HashBytes(''md5'',  coalesce(cast(
    
    

    concat(concat(coalesce(cast(_airbyte_conflict_stream_name_hashid as 
    VARCHAR(max)), ''''), ''-'', coalesce(cast(conflict_stream_name as 
    VARCHAR(max)), ''''),''''), '''') as 
    VARCHAR(max)), '''')), 2) as _airbyte_conflict_stream_name_2_hashid,
    tmp.*
from __dbt__CTE__conflict_stream_name_conflict_stream_name_ab2 tmp
-- conflict_stream_name at conflict_stream_name/conflict_stream_name
)-- Final base SQL model
select
    _airbyte_conflict_stream_name_hashid,
    conflict_stream_name,
    _airbyte_emitted_at,
    _airbyte_conflict_stream_name_2_hashid
from __dbt__CTE__conflict_stream_name_conflict_stream_name_ab3
-- conflict_stream_name at conflict_stream_name/conflict_stream_name from "test_normalization".test_normalization."conflict_stream_name"
    ');

   SELECT * INTO "test_normalization".test_normalization."conflict_stream_name_conflict_stream_name__dbt_tmp" FROM
    "test_normalization".test_normalization."conflict_stream_name_conflict_stream_name__dbt_tmp_temp_view"

   
   
  USE [test_normalization];
  if object_id ('test_normalization."conflict_stream_name_conflict_stream_name__dbt_tmp_temp_view"','V') is not null
      begin
      drop view test_normalization."conflict_stream_name_conflict_stream_name__dbt_tmp_temp_view"
      end

    
   use [test_normalization];
  if EXISTS (
        SELECT * FROM
        sys.indexes WHERE name = 'test_normalization_conflict_stream_name_conflict_stream_name__dbt_tmp_cci'
        AND object_id=object_id('test_normalization_conflict_stream_name_conflict_stream_name__dbt_tmp')
    )
  DROP index test_normalization.conflict_stream_name_conflict_stream_name__dbt_tmp.test_normalization_conflict_stream_name_conflict_stream_name__dbt_tmp_cci
  CREATE CLUSTERED COLUMNSTORE INDEX test_normalization_conflict_stream_name_conflict_stream_name__dbt_tmp_cci
    ON test_normalization.conflict_stream_name_conflict_stream_name__dbt_tmp

   

