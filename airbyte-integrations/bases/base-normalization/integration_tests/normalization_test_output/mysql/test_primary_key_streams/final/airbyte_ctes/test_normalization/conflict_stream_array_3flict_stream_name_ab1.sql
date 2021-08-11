
  create view _airbyte_test_normalization.`conflict_stream_array_3flict_stream_name_ab1__dbt_tmp` as (
    
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
            _airbyte_conflict_stream_array_hashid as _airbyte_hashid,
            
            json_extract(conflict_stream_name, concat("$[", numbers.generated_number - 1, "][0]")) as _airbyte_nested_data
        from test_normalization.`conflict_stream_array_conflict_stream_array`
        cross join numbers
        -- only generate the number of records in the cross join that corresponds
        -- to the number of items in conflict_stream_array_conflict_stream_array.conflict_stream_name
        where numbers.generated_number <= json_length(conflict_stream_name)
    )
select
    _airbyte_conflict_stream_array_2_hashid,
    json_value(_airbyte_nested_data, 
    '$."id"') as id,
    _airbyte_emitted_at
from test_normalization.`conflict_stream_array_conflict_stream_array` as table_alias
left join joined on _airbyte_conflict_stream_array_hashid = joined._airbyte_hashid
where conflict_stream_name is not null
-- conflict_stream_name at conflict_stream_array/conflict_stream_array/conflict_stream_name
  );
