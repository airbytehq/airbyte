
  create or replace  view "AIRBYTE_DATABASE"._AIRBYTE_TEST_NORMALIZATION."UNNEST_ALIAS_AB1"  as (
    
-- SQL model to parse JSON blob stored in a single column and extract into separated field columns as described by the JSON Schema
select
    to_varchar(get_path(parse_json(_airbyte_data), '"id"')) as ID,
    get_path(parse_json(_airbyte_data), '"children"') as CHILDREN,
    _airbyte_emitted_at
from "AIRBYTE_DATABASE".TEST_NORMALIZATION._AIRBYTE_RAW_UNNEST_ALIAS as table_alias
-- UNNEST_ALIAS
  );
