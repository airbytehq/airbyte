

  create  table
    "integrationtests".test_normalization."conflict_stream_array_conflict_stream_array_conflict_stream_name__dbt_tmp"
    
    
  as (
    
with __dbt__CTE__conflict_stream_array_conflict_stream_array_conflict_stream_name_ab1 as (

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
        json_extract_array_element_text(conflict_stream_name, numbers.generated_number::int - 1, true) as _airbyte_nested_data
    from "integrationtests".test_normalization."conflict_stream_array_conflict_stream_array"
    cross join numbers
    -- only generate the number of records in the cross join that corresponds
    -- to the number of items in conflict_stream_array_conflict_stream_array.conflict_stream_name
    where numbers.generated_number <= json_array_length(conflict_stream_name, true)
)
select
    _airbyte_conflict_stream_array_2_hashid,
    case when json_extract_path_text(_airbyte_nested_data, 'id', true) != '' then json_extract_path_text(_airbyte_nested_data, 'id', true) end as id,
    _airbyte_emitted_at
from "integrationtests".test_normalization."conflict_stream_array_conflict_stream_array" as table_alias
left join joined on _airbyte_conflict_stream_array_hashid = joined._airbyte_hashid
where conflict_stream_name is not null
-- conflict_stream_name at conflict_stream_array/conflict_stream_array/conflict_stream_name
),  __dbt__CTE__conflict_stream_array_conflict_stream_array_conflict_stream_name_ab2 as (

-- SQL model to cast each column to its adequate SQL type converted from the JSON schema type
select
    _airbyte_conflict_stream_array_2_hashid,
    cast(id as 
    bigint
) as id,
    _airbyte_emitted_at
from __dbt__CTE__conflict_stream_array_conflict_stream_array_conflict_stream_name_ab1
-- conflict_stream_name at conflict_stream_array/conflict_stream_array/conflict_stream_name
),  __dbt__CTE__conflict_stream_array_conflict_stream_array_conflict_stream_name_ab3 as (

-- SQL model to build a hash column based on the values of this record
select
    *,
    md5(cast(
    
    coalesce(cast(_airbyte_conflict_stream_array_2_hashid as varchar), '') || '-' || coalesce(cast(id as varchar), '')

 as varchar)) as _airbyte_conflict_stream_name_hashid
from __dbt__CTE__conflict_stream_array_conflict_stream_array_conflict_stream_name_ab2
-- conflict_stream_name at conflict_stream_array/conflict_stream_array/conflict_stream_name
)-- Final base SQL model
select
    _airbyte_conflict_stream_array_2_hashid,
    id,
    _airbyte_emitted_at,
    _airbyte_conflict_stream_name_hashid
from __dbt__CTE__conflict_stream_array_conflict_stream_array_conflict_stream_name_ab3
-- conflict_stream_name at conflict_stream_array/conflict_stream_array/conflict_stream_name from "integrationtests".test_normalization."conflict_stream_array_conflict_stream_array"
  );