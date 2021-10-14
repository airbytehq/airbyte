{{ config(schema="test_normalization", tags=["top-level-intermediate"]) }}
-- SQL model to prepare for deduplicating records based on the hash record column
select
  row_number() over (
    partition by {{ quote('_AIRBYTE_POS_DEDUP_CDCX_HASHID') }}
    order by {{ quote('_AIRBYTE_EMITTED_AT') }} asc
  ) as {{ quote('_AIRBYTE_ROW_NUM') }},
  tmp.*
from {{ ref('pos_dedup_cdcx_ab3') }} tmp
-- pos_dedup_cdcx from {{ source('test_normalization', 'airbyte_raw_pos_dedup_cdcx') }}

