USE [test_normalization];
    execute('create view _airbyte_test_normalization."unnest_alias_children_owner_ab3__dbt_tmp" as
    
-- SQL model to build a hash column based on the values of this record
select
    convert(varchar(32), HashBytes(''md5'',  coalesce(cast(
    
    

    concat(concat(coalesce(cast(_airbyte_children_hashid as 
    VARCHAR(max)), ''''), ''-'', coalesce(cast(owner_id as 
    VARCHAR(max)), ''''),''''), '''') as 
    VARCHAR(max)), '''')), 2) as _airbyte_owner_hashid,
    tmp.*
from "test_normalization"._airbyte_test_normalization."unnest_alias_children_owner_ab2" tmp
-- owner at unnest_alias/children/owner
where 1 = 1
    ');

