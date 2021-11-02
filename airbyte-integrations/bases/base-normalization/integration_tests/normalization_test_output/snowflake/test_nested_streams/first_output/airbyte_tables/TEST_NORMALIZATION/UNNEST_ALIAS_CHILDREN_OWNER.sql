

      create or replace transient table "AIRBYTE_DATABASE".TEST_NORMALIZATION."UNNEST_ALIAS_CHILDREN_OWNER"  as
      (select * from(
            
-- Final base SQL model
select
    _AIRBYTE_CHILDREN_HASHID,
    OWNER_ID,
    _AIRBYTE_AB_ID,
    _AIRBYTE_EMITTED_AT,
    convert_timezone('UTC', current_timestamp()) as _AIRBYTE_NORMALIZED_AT,
    _AIRBYTE_OWNER_HASHID
from "AIRBYTE_DATABASE"._AIRBYTE_TEST_NORMALIZATION."UNNEST_ALIAS_CHILDREN_OWNER_AB3"
-- OWNER at unnest_alias/children/owner from "AIRBYTE_DATABASE".TEST_NORMALIZATION."UNNEST_ALIAS_CHILDREN"
where 1 = 1
            ) order by (_AIRBYTE_EMITTED_AT)
      );
    alter table "AIRBYTE_DATABASE".TEST_NORMALIZATION."UNNEST_ALIAS_CHILDREN_OWNER" cluster by (_AIRBYTE_EMITTED_AT);