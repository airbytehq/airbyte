
  create or replace  view "AIRBYTE_DATABASE"._AIRBYTE_TEST_NORMALIZATION."UNNEST_ALIAS_CHILDREN_OWNER_AB1"  as (
    
-- SQL model to parse JSON blob stored in a single column and extract into separated field columns as described by the JSON Schema
select
    _AIRBYTE_CHILDREN_HASHID,
    to_varchar(get_path(parse_json(OWNER), '"owner_id"')) as OWNER_ID,
    _airbyte_emitted_at
from "AIRBYTE_DATABASE".TEST_NORMALIZATION."UNNEST_ALIAS_CHILDREN" as table_alias
where OWNER is not null
-- OWNER at unnest_alias/children/owner
  );
