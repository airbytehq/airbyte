USE [test_normalization];
    execute('create view _airbyte_test_normalization."renamed_dedup_cdc_excluded_ab3__dbt_tmp" as
    
-- SQL model to build a hash column based on the values of this record
select
    convert(varchar(32), HashBytes(''md5'',  coalesce(cast(
    
    

    concat(concat(coalesce(cast(id as 
    VARCHAR(max)), ''''),''''), '''') as 
    VARCHAR(max)), '''')), 2) as _airbyte_renamed_dedup_cdc_excluded_hashid,
    tmp.*
from "test_normalization"._airbyte_test_normalization."renamed_dedup_cdc_excluded_ab2" tmp
-- renamed_dedup_cdc_excluded
where 1 = 1

    ');

