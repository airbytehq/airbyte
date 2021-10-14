USE [test_normalization];
    execute('create view _airbyte_test_normalization."unnest_alias_children_ab3__dbt_tmp" as
    
-- SQL model to build a hash column based on the values of this record
select
    convert(varchar(32), HashBytes(''md5'',  coalesce(cast(
    
    

    concat(concat(coalesce(cast(_airbyte_unnest_alias_hashid as 
    VARCHAR(max)), ''''), ''-'', coalesce(cast(ab_id as 
    VARCHAR(max)), ''''), ''-'', coalesce(cast(owner as 
    VARCHAR(max)), ''''),''''), '''') as 
    VARCHAR(max)), '''')), 2) as _airbyte_children_hashid,
    tmp.*
from "test_normalization"._airbyte_test_normalization."unnest_alias_children_ab2" tmp
-- children at unnest_alias/children
    ');

