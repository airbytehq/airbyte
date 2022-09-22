

  create  table
    test_normalization.`nested_stream_with_co___names_partition_data__dbt_tmp`
  as (
    
with __dbt__cte__nested_stream_with_co_3es_partition_data_ab1 as (

-- SQL model to parse JSON blob stored in a single column and extract into separated field columns as described by the JSON Schema
-- depends_on: test_normalization.`nested_stream_with_co___long_names_partition`
with numbers as (
        

    

    with p as (
        select 0 as generated_number union all select 1
    ), unioned as (

    select

    
    p0.generated_number * power(2, 0)
    
    
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
            
            json_extract(`DATA`, concat("$[", numbers.generated_number - 1, "][0]")) as _airbyte_nested_data
        from test_normalization.`nested_stream_with_co___long_names_partition`
        cross join numbers
        -- only generate the number of records in the cross join that corresponds
        -- to the number of items in test_normalization.`nested_stream_with_co___long_names_partition`.`DATA`
        where numbers.generated_number <= json_length(`DATA`)
    )
select
    _airbyte_partition_hashid,
    json_value(_airbyte_nested_data, 
    '$."currency"' RETURNING CHAR) as currency,
    _airbyte_ab_id,
    _airbyte_emitted_at,
    
    CURRENT_TIMESTAMP
 as _airbyte_normalized_at
from test_normalization.`nested_stream_with_co___long_names_partition` as table_alias
-- DATA at nested_stream_with_complex_columns_resulting_into_long_names/partition/DATA
left join joined on _airbyte_partition_hashid = joined._airbyte_hashid
where 1 = 1
and `DATA` is not null

),  __dbt__cte__nested_stream_with_co_3es_partition_data_ab2 as (

-- SQL model to cast each column to its adequate SQL type converted from the JSON schema type
-- depends_on: __dbt__cte__nested_stream_with_co_3es_partition_data_ab1
select
    _airbyte_partition_hashid,
    cast(currency as char(1024)) as currency,
    _airbyte_ab_id,
    _airbyte_emitted_at,
    
    CURRENT_TIMESTAMP
 as _airbyte_normalized_at
from __dbt__cte__nested_stream_with_co_3es_partition_data_ab1
-- DATA at nested_stream_with_complex_columns_resulting_into_long_names/partition/DATA
where 1 = 1

),  __dbt__cte__nested_stream_with_co_3es_partition_data_ab3 as (

-- SQL model to build a hash column based on the values of this record
-- depends_on: __dbt__cte__nested_stream_with_co_3es_partition_data_ab2
select
    md5(cast(concat(coalesce(cast(_airbyte_partition_hashid as char), ''), '-', coalesce(cast(currency as char), '')) as char)) as _airbyte_data_hashid,
    tmp.*
from __dbt__cte__nested_stream_with_co_3es_partition_data_ab2 tmp
-- DATA at nested_stream_with_complex_columns_resulting_into_long_names/partition/DATA
where 1 = 1

)-- Final base SQL model
-- depends_on: __dbt__cte__nested_stream_with_co_3es_partition_data_ab3
select
    _airbyte_partition_hashid,
    currency,
    _airbyte_ab_id,
    _airbyte_emitted_at,
    
    CURRENT_TIMESTAMP
 as _airbyte_normalized_at,
    _airbyte_data_hashid
from __dbt__cte__nested_stream_with_co_3es_partition_data_ab3
-- DATA at nested_stream_with_complex_columns_resulting_into_long_names/partition/DATA from test_normalization.`nested_stream_with_co___long_names_partition`
where 1 = 1

  )
