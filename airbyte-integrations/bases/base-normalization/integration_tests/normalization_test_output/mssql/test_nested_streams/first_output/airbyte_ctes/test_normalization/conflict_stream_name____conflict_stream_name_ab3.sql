USE [test_normalization];
    execute('create view _airbyte_test_normalization."conflict_stream_name____conflict_stream_name_ab3__dbt_tmp" as
    
-- SQL model to build a hash column based on the values of this record
select
    convert(varchar(32), HashBytes(''md5'',  coalesce(cast(
    
    

    concat(concat(coalesce(cast(_airbyte_conflict_stream_name_2_hashid as 
    VARCHAR(max)), ''''), ''-'', coalesce(cast(groups as 
    VARCHAR(max)), ''''),''''), '''') as 
    VARCHAR(max)), '''')), 2) as _airbyte_conflict_stream_name_3_hashid,
    tmp.*
from "test_normalization"._airbyte_test_normalization."conflict_stream_name____conflict_stream_name_ab2" tmp
-- conflict_stream_name at conflict_stream_name/conflict_stream_name/conflict_stream_name
where 1 = 1
    ');

