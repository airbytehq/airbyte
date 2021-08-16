

  create  table
    "integrationtests".test_normalization."nested_stream_with_complex_columns_resulting_into_long_names_partition_data__dbt_tmp"
    
    
  as (
    
with __dbt__CTE__nested_stream_with_complex_columns_resulting_into_long_names_partition_data_ab1 as (

-- SQL model to parse JSON blob stored in a single column and extract into separated field columns as described by the JSON Schema
with numbers as (
    

    

    with p as (
        select 0 as generated_number union all select 1
    ), unioned as (

    select

    
    p0.generated_number * pow(2, 0)
    
    
    + 1
    as generated_number

    from

    
    p as p0
    
    

    )

    select *
    from unioned
    where generated_number <= 1
    order by generated_number


),
joined as (
    select
        _airbyte_partition_hashid as _airbyte_hashid,
        json_extract_array_element_text(data, numbers.generated_number::int - 1, true) as _airbyte_nested_data
    from "integrationtests".test_normalization."nested_stream_with_complex_columns_resulting_into_long_names_partition"
    cross join numbers
    -- only generate the number of records in the cross join that corresponds
    -- to the number of items in nested_stream_with_complex_columns_resulting_into_long_names_partition.data
    where numbers.generated_number <= json_array_length(data, true)
)
select
    _airbyte_partition_hashid,
    case when json_extract_path_text(_airbyte_nested_data, 'currency', true) != '' then json_extract_path_text(_airbyte_nested_data, 'currency', true) end as currency,
    _airbyte_emitted_at
from "integrationtests".test_normalization."nested_stream_with_complex_columns_resulting_into_long_names_partition" as table_alias
left join joined on _airbyte_partition_hashid = joined._airbyte_hashid
where data is not null
-- data at nested_stream_with_complex_columns_resulting_into_long_names/partition/DATA
),  __dbt__CTE__nested_stream_with_complex_columns_resulting_into_long_names_partition_data_ab2 as (

-- SQL model to cast each column to its adequate SQL type converted from the JSON schema type
select
    _airbyte_partition_hashid,
    cast(currency as varchar) as currency,
    _airbyte_emitted_at
from __dbt__CTE__nested_stream_with_complex_columns_resulting_into_long_names_partition_data_ab1
-- data at nested_stream_with_complex_columns_resulting_into_long_names/partition/DATA
),  __dbt__CTE__nested_stream_with_complex_columns_resulting_into_long_names_partition_data_ab3 as (

-- SQL model to build a hash column based on the values of this record
select
    *,
    md5(cast(
    
    coalesce(cast(_airbyte_partition_hashid as varchar), '') || '-' || coalesce(cast(currency as varchar), '')

 as varchar)) as _airbyte_data_hashid
from __dbt__CTE__nested_stream_with_complex_columns_resulting_into_long_names_partition_data_ab2
-- data at nested_stream_with_complex_columns_resulting_into_long_names/partition/DATA
)-- Final base SQL model
select
    _airbyte_partition_hashid,
    currency,
    _airbyte_emitted_at,
    _airbyte_data_hashid
from __dbt__CTE__nested_stream_with_complex_columns_resulting_into_long_names_partition_data_ab3
-- data at nested_stream_with_complex_columns_resulting_into_long_names/partition/DATA from "integrationtests".test_normalization."nested_stream_with_complex_columns_resulting_into_long_names_partition"
  );