

  create  table
    test_normalization.`nested_stream_with_co__column___with__quotes__dbt_tmp`
  as (
    
with __dbt__CTE__nested_stream_with_co_3mn___with__quotes_ab1 as (

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
            
            json_extract(`column__'with"_quotes`, concat("$[", numbers.generated_number - 1, "][0]")) as _airbyte_nested_data
        from test_normalization.`nested_stream_with_co___long_names_partition`
        cross join numbers
        -- only generate the number of records in the cross join that corresponds
        -- to the number of items in nested_stream_with_co___long_names_partition.`column__'with"_quotes`
        where numbers.generated_number <= json_length(`column__'with"_quotes`)
    )
select
    _airbyte_partition_hashid,
    json_value(_airbyte_nested_data, 
    '$."currency"') as currency,
    _airbyte_emitted_at
from test_normalization.`nested_stream_with_co___long_names_partition` as table_alias
left join joined on _airbyte_partition_hashid = joined._airbyte_hashid
where `column__'with"_quotes` is not null
-- column___with__quotes at nested_stream_with_complex_columns_resulting_into_long_names/partition/column`_'with"_quotes
),  __dbt__CTE__nested_stream_with_co_3mn___with__quotes_ab2 as (

-- SQL model to cast each column to its adequate SQL type converted from the JSON schema type
select
    _airbyte_partition_hashid,
    cast(currency as char) as currency,
    _airbyte_emitted_at
from __dbt__CTE__nested_stream_with_co_3mn___with__quotes_ab1
-- column___with__quotes at nested_stream_with_complex_columns_resulting_into_long_names/partition/column`_'with"_quotes
),  __dbt__CTE__nested_stream_with_co_3mn___with__quotes_ab3 as (

-- SQL model to build a hash column based on the values of this record
select
    md5(cast(concat(coalesce(cast(_airbyte_partition_hashid as char), ''), '-', coalesce(cast(currency as char), '')) as char)) as _airbyte_column___with__quotes_hashid,
    tmp.*
from __dbt__CTE__nested_stream_with_co_3mn___with__quotes_ab2 tmp
-- column___with__quotes at nested_stream_with_complex_columns_resulting_into_long_names/partition/column`_'with"_quotes
)-- Final base SQL model
select
    _airbyte_partition_hashid,
    currency,
    _airbyte_emitted_at,
    _airbyte_column___with__quotes_hashid
from __dbt__CTE__nested_stream_with_co_3mn___with__quotes_ab3
-- column___with__quotes at nested_stream_with_complex_columns_resulting_into_long_names/partition/column`_'with"_quotes from test_normalization.`nested_stream_with_co___long_names_partition`
  )
