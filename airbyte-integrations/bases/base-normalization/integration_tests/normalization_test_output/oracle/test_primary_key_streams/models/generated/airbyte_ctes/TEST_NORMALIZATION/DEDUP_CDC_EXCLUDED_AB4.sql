{{ config(schema="TEST_NORMALIZATION", tags=["top-level-intermediate"]) }}
-- SQL model to prepare for deduplicating records based on the hash record column
select
  row_number() over (
    partition by {{ QUOTE('_AIRBYTE_DEDUP_CDC_EXCLUDED_HASHID') }}
    order by airbyte_emitted_at asc
  ) as airbyte_row_num,
  tmp.*
from {{ ref('DEDUP_CDC_EXCLUDED_AB3') }} tmp
-- DEDUP_CDC_EXCLUDED from {{ source('TEST_NORMALIZATION', 'AIRBYTE_RAW_DEDUP_CDC_EXCLUDED') }}

