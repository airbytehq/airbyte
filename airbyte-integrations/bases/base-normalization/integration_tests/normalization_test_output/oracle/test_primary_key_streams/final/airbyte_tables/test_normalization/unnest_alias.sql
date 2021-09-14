

  create  table test_normalization.unnest_alias__dbt_tmp
  
  as
    
with dbt__cte__unnest_alias_ab1__ as (

-- SQL model to parse JSON blob stored in a single column and extract into separated field columns as described by the JSON Schema
select
    json_value("_AIRBYTE_DATA", '$."id"') as id,
    json_value("_AIRBYTE_DATA", '$."children"') as children,
    "_AIRBYTE_EMITTED_AT"
from test_normalization.airbyte_raw_unnest_alias 
-- unnest_alias
),  dbt__cte__unnest_alias_ab2__ as (

-- SQL model to cast each column to its adequate SQL type converted from the JSON schema type
select
    cast(id as 
    numeric
) as id,
    children,
    "_AIRBYTE_EMITTED_AT"
from dbt__cte__unnest_alias_ab1__
-- unnest_alias
),  dbt__cte__unnest_alias_ab3__ as (

-- SQL model to build a hash column based on the values of this record
select
    ora_hash(
            
                id || '~' ||
            
            
                cast(children as varchar2(4000))
            
    ) as "_AIRBYTE_UNNEST_ALIAS_HASHID",
    tmp.*
from dbt__cte__unnest_alias_ab2__ tmp
-- unnest_alias
)-- Final base SQL model
select
    id,
    children,
    "_AIRBYTE_EMITTED_AT",
    "_AIRBYTE_UNNEST_ALIAS_HASHID"
from dbt__cte__unnest_alias_ab3__
-- unnest_alias from test_normalization.airbyte_raw_unnest_alias