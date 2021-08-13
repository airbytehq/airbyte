

      create or replace transient table "AIRBYTE_DATABASE".TEST_NORMALIZATION."EXCHANGE_RATE"  as
      (
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
    _airbyte_emitted_at,
    _AIRBYTE_EXCHANGE_RATE_HASHID
from "AIRBYTE_DATABASE"._AIRBYTE_TEST_NORMALIZATION."EXCHANGE_RATE_AB3"
-- EXCHANGE_RATE from "AIRBYTE_DATABASE".TEST_NORMALIZATION._AIRBYTE_RAW_EXCHANGE_RATE
      );
    