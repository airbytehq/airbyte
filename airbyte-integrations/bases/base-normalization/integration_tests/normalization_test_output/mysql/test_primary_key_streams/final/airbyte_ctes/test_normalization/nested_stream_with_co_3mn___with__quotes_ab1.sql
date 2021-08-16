
  create view _airbyte_test_normalization.`nested_stream_with_co_3mn___with__quotes_ab1__dbt_tmp` as (
    
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
  );
