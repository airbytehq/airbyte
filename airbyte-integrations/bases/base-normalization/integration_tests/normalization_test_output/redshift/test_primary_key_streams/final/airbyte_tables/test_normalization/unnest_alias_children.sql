

  create  table
    "integrationtests".test_normalization."unnest_alias_children__dbt_tmp"
    
    
  as (
    
with __dbt__CTE__unnest_alias_children_ab1 as (

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
    where generated_number <= 2
    order by generated_number


),
joined as (
    select
        _airbyte_unnest_alias_hashid as _airbyte_hashid,
        json_extract_array_element_text(children, numbers.generated_number::int - 1, true) as _airbyte_nested_data
    from "integrationtests".test_normalization."unnest_alias"
    cross join numbers
    -- only generate the number of records in the cross join that corresponds
    -- to the number of items in unnest_alias.children
    where numbers.generated_number <= json_array_length(children, true)
)
select
    _airbyte_unnest_alias_hashid,
    case when json_extract_path_text(_airbyte_nested_data, 'ab_id', true) != '' then json_extract_path_text(_airbyte_nested_data, 'ab_id', true) end as ab_id,
    
        case when json_extract_path_text(_airbyte_nested_data, 'owner', true) != '' then json_extract_path_text(_airbyte_nested_data, 'owner', true) end
     as owner,
    _airbyte_emitted_at
from "integrationtests".test_normalization."unnest_alias" as table_alias
left join joined on _airbyte_unnest_alias_hashid = joined._airbyte_hashid
where children is not null
-- children at unnest_alias/children
),  __dbt__CTE__unnest_alias_children_ab2 as (

-- SQL model to cast each column to its adequate SQL type converted from the JSON schema type
select
    _airbyte_unnest_alias_hashid,
    cast(ab_id as 
    bigint
) as ab_id,
    cast(owner as varchar) as owner,
    _airbyte_emitted_at
from __dbt__CTE__unnest_alias_children_ab1
-- children at unnest_alias/children
),  __dbt__CTE__unnest_alias_children_ab3 as (

-- SQL model to build a hash column based on the values of this record
select
    *,
    md5(cast(
    
    coalesce(cast(_airbyte_unnest_alias_hashid as varchar), '') || '-' || coalesce(cast(ab_id as varchar), '') || '-' || coalesce(cast(owner as varchar), '')

 as varchar)) as _airbyte_children_hashid
from __dbt__CTE__unnest_alias_children_ab2
-- children at unnest_alias/children
)-- Final base SQL model
select
    _airbyte_unnest_alias_hashid,
    ab_id,
    owner,
    _airbyte_emitted_at,
    _airbyte_children_hashid
from __dbt__CTE__unnest_alias_children_ab3
-- children at unnest_alias/children from "integrationtests".test_normalization."unnest_alias"
  );