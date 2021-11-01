
  create or replace  view "AIRBYTE_DATABASE"._AIRBYTE_TEST_NORMALIZATION."UNNEST_ALIAS_CHILDREN_AB2"  as (
    
-- SQL model to cast each column to its adequate SQL type converted from the JSON schema type
select
    _AIRBYTE_UNNEST_ALIAS_HASHID,
    cast(AB_ID as 
    bigint
) as AB_ID,
    cast(OWNER as 
    variant
) as OWNER,
    _AIRBYTE_AB_ID,
    _AIRBYTE_EMITTED_AT,
    convert_timezone('UTC', current_timestamp()) as _AIRBYTE_NORMALIZED_AT
from "AIRBYTE_DATABASE"._AIRBYTE_TEST_NORMALIZATION."UNNEST_ALIAS_CHILDREN_AB1"
-- CHILDREN at unnest_alias/children
where 1 = 1
  );
