
   
  USE [test_normalization];
  if object_id ('test_normalization."unnest_alias__dbt_tmp_temp_view"','V') is not null
      begin
      drop view test_normalization."unnest_alias__dbt_tmp_temp_view"
      end


   
   
  USE [test_normalization];
  if object_id ('test_normalization."unnest_alias__dbt_tmp"','U') is not null
      begin
      drop table test_normalization."unnest_alias__dbt_tmp"
      end


   USE [test_normalization];
   EXEC('create view test_normalization."unnest_alias__dbt_tmp_temp_view" as
    
with __dbt__CTE__unnest_alias_ab1 as (

-- SQL model to parse JSON blob stored in a single column and extract into separated field columns as described by the JSON Schema
select
    json_value(_airbyte_data, ''$."id"'') as id,
    json_query(_airbyte_data, ''$."children"'') as children,
    _airbyte_emitted_at
from "test_normalization".test_normalization._airbyte_raw_unnest_alias as table_alias
-- unnest_alias
),  __dbt__CTE__unnest_alias_ab2 as (

-- SQL model to cast each column to its adequate SQL type converted from the JSON schema type
select
    cast(id as 
    bigint
) as id,
    children,
    _airbyte_emitted_at
from __dbt__CTE__unnest_alias_ab1
-- unnest_alias
),  __dbt__CTE__unnest_alias_ab3 as (

-- SQL model to build a hash column based on the values of this record
select
    convert(varchar(32), HashBytes(''md5'',  coalesce(cast(
    
    

    concat(concat(coalesce(cast(id as 
    VARCHAR(max)), ''''), ''-'', coalesce(cast(cast(children as 
    VARCHAR(max)) as 
    VARCHAR(max)), ''''),''''), '''') as 
    VARCHAR(max)), '''')), 2) as _airbyte_unnest_alias_hashid,
    tmp.*
from __dbt__CTE__unnest_alias_ab2 tmp
-- unnest_alias
)-- Final base SQL model
select
    id,
    children,
    _airbyte_emitted_at,
    _airbyte_unnest_alias_hashid
from __dbt__CTE__unnest_alias_ab3
-- unnest_alias from "test_normalization".test_normalization._airbyte_raw_unnest_alias
    ');

   SELECT * INTO "test_normalization".test_normalization."unnest_alias__dbt_tmp" FROM
    "test_normalization".test_normalization."unnest_alias__dbt_tmp_temp_view"

   
   
  USE [test_normalization];
  if object_id ('test_normalization."unnest_alias__dbt_tmp_temp_view"','V') is not null
      begin
      drop view test_normalization."unnest_alias__dbt_tmp_temp_view"
      end

    
   use [test_normalization];
  if EXISTS (
        SELECT * FROM
        sys.indexes WHERE name = 'test_normalization_unnest_alias__dbt_tmp_cci'
        AND object_id=object_id('test_normalization_unnest_alias__dbt_tmp')
    )
  DROP index test_normalization.unnest_alias__dbt_tmp.test_normalization_unnest_alias__dbt_tmp_cci
  CREATE CLUSTERED COLUMNSTORE INDEX test_normalization_unnest_alias__dbt_tmp_cci
    ON test_normalization.unnest_alias__dbt_tmp

   

