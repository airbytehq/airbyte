USE [test_normalization];
    execute('create view _airbyte_test_normalization."non_nested_stream_wit__lting_into_long_names_ab3__dbt_tmp" as
    
-- SQL model to build a hash column based on the values of this record
select
    convert(varchar(32), HashBytes(''md5'',  coalesce(cast(
    
    

    concat(concat(coalesce(cast(id as 
    VARCHAR(max)), ''''), ''-'', coalesce(cast("date" as 
    VARCHAR(max)), ''''),''''), '''') as 
    VARCHAR(max)), '''')), 2) as _airbyte_non_nested_s__nto_long_names_hashid,
    tmp.*
from "test_normalization"._airbyte_test_normalization."non_nested_stream_wit__lting_into_long_names_ab2" tmp
-- non_nested_stream_wit__lting_into_long_names
where 1 = 1
    ');

