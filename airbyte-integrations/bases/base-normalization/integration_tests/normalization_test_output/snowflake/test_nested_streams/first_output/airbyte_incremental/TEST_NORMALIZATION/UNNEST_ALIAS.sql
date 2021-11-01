

      create or replace transient table "AIRBYTE_DATABASE".TEST_NORMALIZATION."UNNEST_ALIAS"  as
      (select * from(
            
-- Final base SQL model
select
    ID,
    CHILDREN,
    _AIRBYTE_AB_ID,
    _AIRBYTE_EMITTED_AT,
    convert_timezone('UTC', current_timestamp()) as _AIRBYTE_NORMALIZED_AT,
    _AIRBYTE_UNNEST_ALIAS_HASHID
from "AIRBYTE_DATABASE"._AIRBYTE_TEST_NORMALIZATION."UNNEST_ALIAS_AB3"
-- UNNEST_ALIAS from "AIRBYTE_DATABASE".TEST_NORMALIZATION._AIRBYTE_RAW_UNNEST_ALIAS
where 1 = 1

            ) order by (_AIRBYTE_EMITTED_AT)
      );
    alter table "AIRBYTE_DATABASE".TEST_NORMALIZATION."UNNEST_ALIAS" cluster by (_AIRBYTE_EMITTED_AT);