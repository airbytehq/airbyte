

      create or replace transient table "AIRBYTE_DATABASE".TEST_NORMALIZATION."EXCHANGE_RATE"  as
      (select * from(
            
-- Final base SQL model
select
    ID,
    CURRENCY,
    DATE,
    TIMESTAMP_COL,
    "HKD@spéçiäl & characters",
    HKD_SPECIAL___CHARACTERS,
    NZD,
    USD,
    _AIRBYTE_AB_ID,
    _AIRBYTE_EMITTED_AT,
    convert_timezone('UTC', current_timestamp()) as _AIRBYTE_NORMALIZED_AT,
    _AIRBYTE_EXCHANGE_RATE_HASHID
from "AIRBYTE_DATABASE"._AIRBYTE_TEST_NORMALIZATION."EXCHANGE_RATE_AB3"
-- EXCHANGE_RATE from "AIRBYTE_DATABASE".TEST_NORMALIZATION._AIRBYTE_RAW_EXCHANGE_RATE
where 1 = 1

            ) order by (_AIRBYTE_EMITTED_AT)
      );
    alter table "AIRBYTE_DATABASE".TEST_NORMALIZATION."EXCHANGE_RATE" cluster by (_AIRBYTE_EMITTED_AT);