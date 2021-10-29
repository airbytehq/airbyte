
  create or replace  view "AIRBYTE_DATABASE"._AIRBYTE_TEST_NORMALIZATION."UNNEST_ALIAS_CHILDREN_AB1"  as (
    
-- SQL model to parse JSON blob stored in a single column and extract into separated field columns as described by the JSON Schema

select
    _AIRBYTE_UNNEST_ALIAS_HASHID,
    to_varchar(get_path(parse_json(CHILDREN.value), '"ab_id"')) as AB_ID,
    
        get_path(parse_json(CHILDREN.value), '"owner"')
     as OWNER,
    _AIRBYTE_AB_ID,
    _AIRBYTE_EMITTED_AT,
    convert_timezone('UTC', current_timestamp()) as _AIRBYTE_NORMALIZED_AT
from "AIRBYTE_DATABASE".TEST_NORMALIZATION."UNNEST_ALIAS" as table_alias
-- CHILDREN at unnest_alias/children
cross join table(flatten(CHILDREN)) as CHILDREN
where 1 = 1
and CHILDREN is not null
  );
