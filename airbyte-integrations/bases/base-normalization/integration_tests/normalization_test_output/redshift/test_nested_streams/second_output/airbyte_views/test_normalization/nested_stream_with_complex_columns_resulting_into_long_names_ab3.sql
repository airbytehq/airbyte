

  create view "integrationtests"._airbyte_test_normalization."nested_stream_with_complex_columns_resulting_into_long_names_ab3__dbt_tmp" as (
    
with __dbt__cte__nested_stream_with_complex_columns_resulting_into_long_names_ab1 as (

-- SQL model to parse JSON blob stored in a single column and extract into separated field columns as described by the JSON Schema
select
    case when json_extract_path_text(_airbyte_data, 'id', true) != '' then json_extract_path_text(_airbyte_data, 'id', true) end as id,
    case when json_extract_path_text(_airbyte_data, 'date', true) != '' then json_extract_path_text(_airbyte_data, 'date', true) end as date,
    
        case when json_extract_path_text(table_alias._airbyte_data, 'partition', true) != '' then json_extract_path_text(table_alias._airbyte_data, 'partition', true) end
     as "partition",
    _airbyte_ab_id,
    _airbyte_emitted_at,
    getdate() as _airbyte_normalized_at
from "integrationtests".test_normalization._airbyte_raw_nested_stream_with_complex_columns_resulting_into_long_names as table_alias
-- nested_stream_with_complex_columns_resulting_into_long_names
where 1 = 1

),  __dbt__cte__nested_stream_with_complex_columns_resulting_into_long_names_ab2 as (

-- SQL model to cast each column to its adequate SQL type converted from the JSON schema type
select
    cast(id as varchar) as id,
    cast(date as varchar) as date,
    cast("partition" as varchar) as "partition",
    _airbyte_ab_id,
    _airbyte_emitted_at,
    getdate() as _airbyte_normalized_at
from __dbt__cte__nested_stream_with_complex_columns_resulting_into_long_names_ab1
-- nested_stream_with_complex_columns_resulting_into_long_names
where 1 = 1

)-- SQL model to build a hash column based on the values of this record
select
    md5(cast(coalesce(cast(id as varchar), '') || '-' || coalesce(cast(date as varchar), '') || '-' || coalesce(cast("partition" as varchar), '') as varchar)) as _airbyte_nested_stream_with_complex_columns_resulting_into_long_names_hashid,
    tmp.*
from __dbt__cte__nested_stream_with_complex_columns_resulting_into_long_names_ab2 tmp
-- nested_stream_with_complex_columns_resulting_into_long_names
where 1 = 1

  ) ;
