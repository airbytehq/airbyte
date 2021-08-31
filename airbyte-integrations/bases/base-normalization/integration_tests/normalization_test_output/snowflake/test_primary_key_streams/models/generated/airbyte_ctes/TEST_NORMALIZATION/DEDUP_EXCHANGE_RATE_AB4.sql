{{ config(schema="_AIRBYTE_TEST_NORMALIZATION", tags=["top-level-intermediate"]) }}
-- SQL model to prepare for deduplicating records based on the hash record column
select
  row_number() over (
    partition by _AIRBYTE_DEDUP_EXCHANGE_RATE_HASHID
    order by _AIRBYTE_EMITTED_AT asc
  ) as _AIRBYTE_ROW_NUM,
  tmp.*
from {{ ref('DEDUP_EXCHANGE_RATE_AB3') }} tmp
-- DEDUP_EXCHANGE_RATE from {{ source('TEST_NORMALIZATION', '_AIRBYTE_RAW_DEDUP_EXCHANGE_RATE') }}

