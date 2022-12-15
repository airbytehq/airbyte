

  create  table "postgres".test_normalization."unnest_alias_childre__column___with__quotes__dbt_tmp"
  as (
    
with __dbt__cte__unnest_alias_childre__column___with__quotes_ab1 as (

-- SQL model to parse JSON blob stored in a single column and extract into separated field columns as described by the JSON Schema
-- depends_on: "postgres".test_normalization."unnest_alias_children_owner"

select
    _airbyte_owner_hashid,
    jsonb_extract_path_text(_airbyte_nested_data, 'currency') as currency,
    _airbyte_ab_id,
    _airbyte_emitted_at,
    now() as _airbyte_normalized_at
from "postgres".test_normalization."unnest_alias_children_owner" as table_alias
-- column___with__quotes at unnest_alias/children/owner/column`_'with"_quotes
cross join jsonb_array_elements(
        case jsonb_typeof("column`_'with""_quotes")
        when 'array' then "column`_'with""_quotes"
        else '[]' end
    ) as _airbyte_nested_data
where 1 = 1
and "column`_'with""_quotes" is not null
),  __dbt__cte__unnest_alias_childre__column___with__quotes_ab2 as (

-- SQL model to cast each column to its adequate SQL type converted from the JSON schema type
-- depends_on: __dbt__cte__unnest_alias_childre__column___with__quotes_ab1
select
    _airbyte_owner_hashid,
    cast(currency as text) as currency,
    _airbyte_ab_id,
    _airbyte_emitted_at,
    now() as _airbyte_normalized_at
from __dbt__cte__unnest_alias_childre__column___with__quotes_ab1
-- column___with__quotes at unnest_alias/children/owner/column`_'with"_quotes
where 1 = 1
),  __dbt__cte__unnest_alias_childre__column___with__quotes_ab3 as (

-- SQL model to build a hash column based on the values of this record
-- depends_on: __dbt__cte__unnest_alias_childre__column___with__quotes_ab2
select
    md5(cast(coalesce(cast(_airbyte_owner_hashid as text), '') || '-' || coalesce(cast(currency as text), '') as text)) as _airbyte_column___with__quotes_hashid,
    tmp.*
from __dbt__cte__unnest_alias_childre__column___with__quotes_ab2 tmp
-- column___with__quotes at unnest_alias/children/owner/column`_'with"_quotes
where 1 = 1
)-- Final base SQL model
-- depends_on: __dbt__cte__unnest_alias_childre__column___with__quotes_ab3
select
    _airbyte_owner_hashid,
    currency,
    _airbyte_ab_id,
    _airbyte_emitted_at,
    now() as _airbyte_normalized_at,
    _airbyte_column___with__quotes_hashid
from __dbt__cte__unnest_alias_childre__column___with__quotes_ab3
-- column___with__quotes at unnest_alias/children/owner/column`_'with"_quotes from "postgres".test_normalization."unnest_alias_children_owner"
where 1 = 1
  );