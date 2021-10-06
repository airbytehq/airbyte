{{ config(schema="_AIRBYTE_TEST_NORMALIZATION", tags=["top-level-intermediate"]) }}
-- SQL model to prepare for deduplicating records based on the hash record column
select
  *,
  row_number() over (
    partition by _AIRBYTE_DEDUP_CDC_EXCLUDED_HASHID
    order by _airbyte_emitted_at asc
  ) as _airbyte_row_num
from {{ ref('DEDUP_CDC_EXCLUDED_AB3') }}
-- DEDUP_CDC_EXCLUDED from {{ source('TEST_NORMALIZATION', '_AIRBYTE_RAW_DEDUP_CDC_EXCLUDED') }}

