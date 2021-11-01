

      create or replace transient table "AIRBYTE_DATABASE".TEST_NORMALIZATION."UNNEST_ALIAS_CHILDREN"  as
      (select * from(
            
-- Final base SQL model
select
    _AIRBYTE_UNNEST_ALIAS_HASHID,
    AB_ID,
    OWNER,
    _AIRBYTE_AB_ID,
    _AIRBYTE_EMITTED_AT,
    convert_timezone('UTC', current_timestamp()) as _AIRBYTE_NORMALIZED_AT,
    _AIRBYTE_CHILDREN_HASHID
from "AIRBYTE_DATABASE"._AIRBYTE_TEST_NORMALIZATION."UNNEST_ALIAS_CHILDREN_AB3"
-- CHILDREN at unnest_alias/children from "AIRBYTE_DATABASE".TEST_NORMALIZATION."UNNEST_ALIAS"
where 1 = 1
            ) order by (_AIRBYTE_EMITTED_AT)
      );
    alter table "AIRBYTE_DATABASE".TEST_NORMALIZATION."UNNEST_ALIAS_CHILDREN" cluster by (_AIRBYTE_EMITTED_AT);