
  create or replace  view "AIRBYTE_DATABASE"._AIRBYTE_TEST_NORMALIZATION."UNNEST_ALIAS_CHILDREN_OWNER_AB1"  as (
    
-- SQL model to parse JSON blob stored in a single column and extract into separated field columns as described by the JSON Schema
select
    _AIRBYTE_CHILDREN_HASHID,
    to_varchar(get_path(parse_json(OWNER), '"owner_id"')) as OWNER_ID,
    _AIRBYTE_AB_ID,
    _AIRBYTE_EMITTED_AT,
    convert_timezone('UTC', current_timestamp()) as _AIRBYTE_NORMALIZED_AT
from "AIRBYTE_DATABASE".TEST_NORMALIZATION."UNNEST_ALIAS_CHILDREN" as table_alias
-- OWNER at unnest_alias/children/owner
where 1 = 1
and OWNER is not null
  );
