USE [test_normalization];
    execute('create view _airbyte_test_normalization."nested_stream_with_co___long_names_partition_ab3__dbt_tmp" as
    
-- SQL model to build a hash column based on the values of this record
select
    convert(varchar(32), HashBytes(''md5'',  coalesce(cast(
    
    

    concat(concat(coalesce(cast(_airbyte_nested_strea__nto_long_names_hashid as 
    VARCHAR(max)), ''''), ''-'', coalesce(cast(cast(double_array_data as 
    VARCHAR(max)) as 
    VARCHAR(max)), ''''), ''-'', coalesce(cast(cast("DATA" as 
    VARCHAR(max)) as 
    VARCHAR(max)), ''''), ''-'', coalesce(cast(cast("column`_''with""_quotes" as 
    VARCHAR(max)) as 
    VARCHAR(max)), ''''),''''), '''') as 
    VARCHAR(max)), '''')), 2) as _airbyte_partition_hashid,
    tmp.*
from "test_normalization"._airbyte_test_normalization."nested_stream_with_co___long_names_partition_ab2" tmp
-- partition at nested_stream_with_complex_columns_resulting_into_long_names/partition
    ');

