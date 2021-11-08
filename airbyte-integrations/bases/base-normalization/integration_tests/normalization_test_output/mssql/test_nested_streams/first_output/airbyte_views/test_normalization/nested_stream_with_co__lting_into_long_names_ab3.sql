USE [test_normalization];
    execute('create view _airbyte_test_normalization."nested_stream_with_co__lting_into_long_names_ab3__dbt_tmp" as
    
with __dbt__CTE__nested_stream_with_co__lting_into_long_names_ab1 as (

-- SQL model to parse JSON blob stored in a single column and extract into separated field columns as described by the JSON Schema
select
    json_value(_airbyte_data, ''$."id"'') as id,
    json_value(_airbyte_data, ''$."date"'') as "date",
    json_query(_airbyte_data, ''$."partition"'') as "partition",
    _airbyte_ab_id,
    _airbyte_emitted_at,
    SYSDATETIME() as _airbyte_normalized_at
from "test_normalization".test_normalization._airbyte_raw_nested_stream_with_complex_columns_resulting_into_long_names as table_alias
-- nested_stream_with_co__lting_into_long_names
where 1 = 1

),  __dbt__CTE__nested_stream_with_co__lting_into_long_names_ab2 as (

-- SQL model to cast each column to its adequate SQL type converted from the JSON schema type
select
    cast(id as 
    VARCHAR(max)) as id,
    cast("date" as 
    VARCHAR(max)) as "date",
    cast("partition" as VARCHAR(max)) as "partition",
    _airbyte_ab_id,
    _airbyte_emitted_at,
    SYSDATETIME() as _airbyte_normalized_at
from __dbt__CTE__nested_stream_with_co__lting_into_long_names_ab1
-- nested_stream_with_co__lting_into_long_names
where 1 = 1

)-- SQL model to build a hash column based on the values of this record
select
    convert(varchar(32), HashBytes(''md5'',  coalesce(cast(
    
    

    concat(concat(coalesce(cast(id as 
    VARCHAR(max)), ''''), ''-'', coalesce(cast("date" as 
    VARCHAR(max)), ''''), ''-'', coalesce(cast("partition" as 
    VARCHAR(max)), ''''),''''), '''') as 
    VARCHAR(max)), '''')), 2) as _airbyte_nested_strea__nto_long_names_hashid,
    tmp.*
from __dbt__CTE__nested_stream_with_co__lting_into_long_names_ab2 tmp
-- nested_stream_with_co__lting_into_long_names
where 1 = 1

    ');

