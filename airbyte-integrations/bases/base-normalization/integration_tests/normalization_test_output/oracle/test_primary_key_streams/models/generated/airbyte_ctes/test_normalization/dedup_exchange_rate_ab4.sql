{{ config(schema="test_normalization", tags=["top-level-intermediate"]) }}
-- SQL model to prepare for deduplicating records based on the hash record column
select
  row_number() over (
    partition by {{ QUOTE('_AIRBYTE_DEDUP_EXCHANGE_RATE_HASHID') }}
    order by airbyte_emitted_at asc
  ) as airbyte_row_num,
  tmp.*
from {{ ref('dedup_exchange_rate_ab3') }} tmp
-- dedup_exchange_rate from {{ source('test_normalization', 'airbyte_raw_dedup_exchange_rate') }}

