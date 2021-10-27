USE [test_normalization];
    execute('create view _airbyte_test_normalization."pos_dedup_cdcx_ab3__dbt_tmp" as
    
-- SQL model to build a hash column based on the values of this record
select
    convert(varchar(32), HashBytes(''md5'',  coalesce(cast(
    
    

    concat(concat(coalesce(cast(id as 
    VARCHAR(max)), ''''), ''-'', coalesce(cast(name as 
    VARCHAR(max)), ''''), ''-'', coalesce(cast(_ab_cdc_lsn as 
    VARCHAR(max)), ''''), ''-'', coalesce(cast(_ab_cdc_updated_at as 
    VARCHAR(max)), ''''), ''-'', coalesce(cast(_ab_cdc_deleted_at as 
    VARCHAR(max)), ''''), ''-'', coalesce(cast(_ab_cdc_log_pos as 
    VARCHAR(max)), ''''),''''), '''') as 
    VARCHAR(max)), '''')), 2) as _airbyte_pos_dedup_cdcx_hashid,
    tmp.*
from "test_normalization"._airbyte_test_normalization."pos_dedup_cdcx_ab2" tmp
-- pos_dedup_cdcx
    ');

