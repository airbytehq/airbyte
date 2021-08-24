

      create or replace transient table "AIRBYTE_DATABASE".TEST_NORMALIZATION."DEDUP_EXCHANGE_RATE"  as
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
    _AIRBYTE_DEDUP_EXCHANGE_RATE_HASHID
from "AIRBYTE_DATABASE".TEST_NORMALIZATION."DEDUP_EXCHANGE_RATE_SCD"
-- DEDUP_EXCHANGE_RATE from "AIRBYTE_DATABASE".TEST_NORMALIZATION._AIRBYTE_RAW_DEDUP_EXCHANGE_RATE
where _airbyte_active_row = True
      );
    