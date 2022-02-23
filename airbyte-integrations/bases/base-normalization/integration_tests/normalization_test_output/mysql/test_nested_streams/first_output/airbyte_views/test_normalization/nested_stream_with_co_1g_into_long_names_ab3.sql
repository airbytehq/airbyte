
  create view _airbyte_test_normalization.`nested_stream_with_co_1g_into_long_names_ab3__dbt_tmp` as (
    
with __dbt__CTE__nested_stream_with_co_1g_into_long_names_ab1 as (

-- SQL model to parse JSON blob stored in a single column and extract into separated field columns as described by the JSON Schema
select
    json_value(_airbyte_data, 
    '$."id"') as id,
    json_value(_airbyte_data, 
    '$."date"') as `date`,
    
        json_extract(table_alias._airbyte_data, 
    '$."partition"')
     as `partition`,
    _airbyte_ab_id,
    _airbyte_emitted_at,
    
    CURRENT_TIMESTAMP
 as _airbyte_normalized_at
from test_normalization._airbyte_raw_nested_s__lting_into_long_names as table_alias
-- nested_stream_with_co__lting_into_long_names
where 1 = 1

),  __dbt__CTE__nested_stream_with_co_1g_into_long_names_ab2 as (

-- SQL model to cast each column to its adequate SQL type converted from the JSON schema type
select
    cast(id as char) as id,
    cast(`date` as char) as `date`,
    cast(`partition` as json) as `partition`,
    _airbyte_ab_id,
    _airbyte_emitted_at,
    
    CURRENT_TIMESTAMP
 as _airbyte_normalized_at
from __dbt__CTE__nested_stream_with_co_1g_into_long_names_ab1
-- nested_stream_with_co__lting_into_long_names
where 1 = 1

)-- SQL model to build a hash column based on the values of this record
select
    md5(cast(concat(coalesce(cast(id as char), ''), '-', coalesce(cast(`date` as char), ''), '-', coalesce(cast(`partition` as char), '')) as char)) as _airbyte_nested_strea__nto_long_names_hashid,
    tmp.*
from __dbt__CTE__nested_stream_with_co_1g_into_long_names_ab2 tmp
-- nested_stream_with_co__lting_into_long_names
where 1 = 1

  );
