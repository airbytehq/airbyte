
   
  USE [test_normalization];
  if object_id ('test_normalization."unnest_alias_children__dbt_tmp_temp_view"','V') is not null
      begin
      drop view test_normalization."unnest_alias_children__dbt_tmp_temp_view"
      end


   
   
  USE [test_normalization];
  if object_id ('test_normalization."unnest_alias_children__dbt_tmp"','U') is not null
      begin
      drop table test_normalization."unnest_alias_children__dbt_tmp"
      end


   USE [test_normalization];
   EXEC('create view test_normalization."unnest_alias_children__dbt_tmp_temp_view" as
    
with __dbt__CTE__unnest_alias_children_ab1 as (

-- SQL model to parse JSON blob stored in a single column and extract into separated field columns as described by the JSON Schema

select
    _airbyte_unnest_alias_hashid,
    json_value(
    children.value, ''$."ab_id"'') as ab_id,
    json_query(
    children.value, ''$."owner"'') as owner,
    _airbyte_emitted_at
from "test_normalization".test_normalization."unnest_alias" as table_alias

    CROSS APPLY (
	    SELECT [value] = CASE 
			WHEN [type] = 4 THEN (SELECT [value] FROM OPENJSON([value])) 
			WHEN [type] = 5 THEN [value]
			END
	    FROM OPENJSON(children)
    ) AS children
where children is not null
-- children at unnest_alias/children
),  __dbt__CTE__unnest_alias_children_ab2 as (

-- SQL model to cast each column to its adequate SQL type converted from the JSON schema type
select
    _airbyte_unnest_alias_hashid,
    cast(ab_id as 
    bigint
) as ab_id,
    cast(owner as VARCHAR(max)) as owner,
    _airbyte_emitted_at
from __dbt__CTE__unnest_alias_children_ab1
-- children at unnest_alias/children
),  __dbt__CTE__unnest_alias_children_ab3 as (

-- SQL model to build a hash column based on the values of this record
select
    convert(varchar(32), HashBytes(''md5'',  coalesce(cast(
    
    

    concat(concat(coalesce(cast(_airbyte_unnest_alias_hashid as 
    VARCHAR(max)), ''''), ''-'', coalesce(cast(ab_id as 
    VARCHAR(max)), ''''), ''-'', coalesce(cast(owner as 
    VARCHAR(max)), ''''),''''), '''') as 
    VARCHAR(max)), '''')), 2) as _airbyte_children_hashid,
    tmp.*
from __dbt__CTE__unnest_alias_children_ab2 tmp
-- children at unnest_alias/children
)-- Final base SQL model
select
    _airbyte_unnest_alias_hashid,
    ab_id,
    owner,
    _airbyte_emitted_at,
    _airbyte_children_hashid
from __dbt__CTE__unnest_alias_children_ab3
-- children at unnest_alias/children from "test_normalization".test_normalization."unnest_alias"
    ');

   SELECT * INTO "test_normalization".test_normalization."unnest_alias_children__dbt_tmp" FROM
    "test_normalization".test_normalization."unnest_alias_children__dbt_tmp_temp_view"

   
   
  USE [test_normalization];
  if object_id ('test_normalization."unnest_alias_children__dbt_tmp_temp_view"','V') is not null
      begin
      drop view test_normalization."unnest_alias_children__dbt_tmp_temp_view"
      end

    
   use [test_normalization];
  if EXISTS (
        SELECT * FROM
        sys.indexes WHERE name = 'test_normalization_unnest_alias_children__dbt_tmp_cci'
        AND object_id=object_id('test_normalization_unnest_alias_children__dbt_tmp')
    )
  DROP index test_normalization.unnest_alias_children__dbt_tmp.test_normalization_unnest_alias_children__dbt_tmp_cci
  CREATE CLUSTERED COLUMNSTORE INDEX test_normalization_unnest_alias_children__dbt_tmp_cci
    ON test_normalization.unnest_alias_children__dbt_tmp

   

