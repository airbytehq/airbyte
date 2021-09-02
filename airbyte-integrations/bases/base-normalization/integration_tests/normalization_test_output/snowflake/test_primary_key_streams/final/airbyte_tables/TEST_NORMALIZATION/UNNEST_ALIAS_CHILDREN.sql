

      create or replace transient table "AIRBYTE_DATABASE".TEST_NORMALIZATION."UNNEST_ALIAS_CHILDREN"  as
      (
-- Final base SQL model
select
    _AIRBYTE_UNNEST_ALIAS_HASHID,
    AB_ID,
    OWNER,
    _airbyte_emitted_at,
    _AIRBYTE_CHILDREN_HASHID
from "AIRBYTE_DATABASE"._AIRBYTE_TEST_NORMALIZATION."UNNEST_ALIAS_CHILDREN_AB3"
-- CHILDREN at unnest_alias/children from "AIRBYTE_DATABASE".TEST_NORMALIZATION."UNNEST_ALIAS"
      );
    