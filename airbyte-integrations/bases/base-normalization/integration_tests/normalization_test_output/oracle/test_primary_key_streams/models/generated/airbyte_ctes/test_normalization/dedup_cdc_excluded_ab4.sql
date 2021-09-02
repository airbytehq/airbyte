{{ config(schema="test_normalization", tags=["top-level-intermediate"]) }}
-- SQL model to prepare for deduplicating records based on the hash record column
select
  row_number() over (
    partition by {{ quote('_AIRBYTE_DEDUP_CDC_EXCLUDED_HASHID') }}
    order by {{ quote('_AIRBYTE_EMITTED_AT') }} asc
  ) as {{ quote('_AIRBYTE_ROW_NUM') }},
  tmp.*
from {{ ref('dedup_cdc_excluded_ab3') }} tmp
-- dedup_cdc_excluded from {{ source('test_normalization', 'airbyte_raw_dedup_cdc_excluded') }}

