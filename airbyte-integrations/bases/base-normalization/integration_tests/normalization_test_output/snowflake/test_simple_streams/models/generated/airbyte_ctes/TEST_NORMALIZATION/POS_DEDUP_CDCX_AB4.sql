{{ config(schema="_AIRBYTE_TEST_NORMALIZATION", tags=["top-level-intermediate"]) }}
-- SQL model to prepare for deduplicating records based on the hash record column
select
  row_number() over (
    partition by _AIRBYTE_POS_DEDUP_CDCX_HASHID
    order by _AIRBYTE_EMITTED_AT asc
  ) as _AIRBYTE_ROW_NUM,
  tmp.*
from {{ ref('POS_DEDUP_CDCX_AB3') }} tmp
-- POS_DEDUP_CDCX from {{ source('TEST_NORMALIZATION', '_AIRBYTE_RAW_POS_DEDUP_CDCX') }}

