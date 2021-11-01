USE [test_normalization];
    execute('create view _airbyte_test_normalization."exchange_rate_ab3__dbt_tmp" as
    
-- SQL model to build a hash column based on the values of this record
select
    convert(varchar(32), HashBytes(''md5'',  coalesce(cast(
    
    

    concat(concat(coalesce(cast(id as 
    VARCHAR(max)), ''''), ''-'', coalesce(cast(currency as 
    VARCHAR(max)), ''''), ''-'', coalesce(cast("date" as 
    VARCHAR(max)), ''''), ''-'', coalesce(cast(timestamp_col as 
    VARCHAR(max)), ''''), ''-'', coalesce(cast("HKD@spéçiäl & characters" as 
    VARCHAR(max)), ''''), ''-'', coalesce(cast(hkd_special___characters as 
    VARCHAR(max)), ''''), ''-'', coalesce(cast(nzd as 
    VARCHAR(max)), ''''), ''-'', coalesce(cast(usd as 
    VARCHAR(max)), ''''),''''), '''') as 
    VARCHAR(max)), '''')), 2) as _airbyte_exchange_rate_hashid,
    tmp.*
from "test_normalization"._airbyte_test_normalization."exchange_rate_ab2" tmp
-- exchange_rate
where 1 = 1

    ');

