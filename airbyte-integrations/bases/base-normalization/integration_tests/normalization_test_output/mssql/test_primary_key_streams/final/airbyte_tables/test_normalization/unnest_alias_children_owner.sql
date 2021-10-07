
   
  USE [test_normalization];
  if object_id ('test_normalization."unnest_alias_children_owner__dbt_tmp_temp_view"','V') is not null
      begin
      drop view test_normalization."unnest_alias_children_owner__dbt_tmp_temp_view"
      end


   
   
  USE [test_normalization];
  if object_id ('test_normalization."unnest_alias_children_owner__dbt_tmp"','U') is not null
      begin
      drop table test_normalization."unnest_alias_children_owner__dbt_tmp"
      end


   USE [test_normalization];
   EXEC('create view test_normalization."unnest_alias_children_owner__dbt_tmp_temp_view" as
    
with __dbt__CTE__unnest_alias_children_owner_ab1 as (

-- SQL model to parse JSON blob stored in a single column and extract into separated field columns as described by the JSON Schema
select
    _airbyte_children_hashid,
    json_value(owner, ''$."owner_id"'') as owner_id,
    _airbyte_emitted_at
from "test_normalization".test_normalization."unnest_alias_children" as table_alias
where owner is not null
-- owner at unnest_alias/children/owner
),  __dbt__CTE__unnest_alias_children_owner_ab2 as (

-- SQL model to cast each column to its adequate SQL type converted from the JSON schema type
select
    _airbyte_children_hashid,
    cast(owner_id as 
    bigint
) as owner_id,
    _airbyte_emitted_at
from __dbt__CTE__unnest_alias_children_owner_ab1
-- owner at unnest_alias/children/owner
),  __dbt__CTE__unnest_alias_children_owner_ab3 as (

-- SQL model to build a hash column based on the values of this record
select
    convert(varchar(32), HashBytes(''md5'',  coalesce(cast(
    
    

    concat(concat(coalesce(cast(_airbyte_children_hashid as 
    VARCHAR(max)), ''''), ''-'', coalesce(cast(owner_id as 
    VARCHAR(max)), ''''),''''), '''') as 
    VARCHAR(max)), '''')), 2) as _airbyte_owner_hashid,
    tmp.*
from __dbt__CTE__unnest_alias_children_owner_ab2 tmp
-- owner at unnest_alias/children/owner
)-- Final base SQL model
select
    _airbyte_children_hashid,
    owner_id,
    _airbyte_emitted_at,
    _airbyte_owner_hashid
from __dbt__CTE__unnest_alias_children_owner_ab3
-- owner at unnest_alias/children/owner from "test_normalization".test_normalization."unnest_alias_children"
    ');

   SELECT * INTO "test_normalization".test_normalization."unnest_alias_children_owner__dbt_tmp" FROM
    "test_normalization".test_normalization."unnest_alias_children_owner__dbt_tmp_temp_view"

   
   
  USE [test_normalization];
  if object_id ('test_normalization."unnest_alias_children_owner__dbt_tmp_temp_view"','V') is not null
      begin
      drop view test_normalization."unnest_alias_children_owner__dbt_tmp_temp_view"
      end

    
   use [test_normalization];
  if EXISTS (
        SELECT * FROM
        sys.indexes WHERE name = 'test_normalization_unnest_alias_children_owner__dbt_tmp_cci'
        AND object_id=object_id('test_normalization_unnest_alias_children_owner__dbt_tmp')
    )
  DROP index test_normalization.unnest_alias_children_owner__dbt_tmp.test_normalization_unnest_alias_children_owner__dbt_tmp_cci
  CREATE CLUSTERED COLUMNSTORE INDEX test_normalization_unnest_alias_children_owner__dbt_tmp_cci
    ON test_normalization.unnest_alias_children_owner__dbt_tmp

   

