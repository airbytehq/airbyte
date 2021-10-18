USE [test_normalization];
    execute('create view _airbyte_test_normalization."conflict_stream_scalar_ab3__dbt_tmp" as
    
-- SQL model to build a hash column based on the values of this record
select
    convert(varchar(32), HashBytes(''md5'',  coalesce(cast(
    
    

    concat(concat(coalesce(cast(id as 
    VARCHAR(max)), ''''), ''-'', coalesce(cast(conflict_stream_scalar as 
    VARCHAR(max)), ''''),''''), '''') as 
    VARCHAR(max)), '''')), 2) as _airbyte_conflict_stream_scalar_hashid,
    tmp.*
from "test_normalization"._airbyte_test_normalization."conflict_stream_scalar_ab2" tmp
-- conflict_stream_scalar
    ');

