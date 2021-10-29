USE [test_normalization];
    execute('create view _airbyte_test_normalization."nested_stream_with_co__ion_double_array_data_ab3__dbt_tmp" as
    
-- SQL model to build a hash column based on the values of this record
select
    convert(varchar(32), HashBytes(''md5'',  coalesce(cast(
    
    

    concat(concat(coalesce(cast(_airbyte_partition_hashid as 
    VARCHAR(max)), ''''), ''-'', coalesce(cast(id as 
    VARCHAR(max)), ''''),''''), '''') as 
    VARCHAR(max)), '''')), 2) as _airbyte_double_array_data_hashid,
    tmp.*
from "test_normalization"._airbyte_test_normalization."nested_stream_with_co__ion_double_array_data_ab2" tmp
-- double_array_data at nested_stream_with_complex_columns_resulting_into_long_names/partition/double_array_data
where 1 = 1
    ');

