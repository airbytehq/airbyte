{{ config(schema="_airbyte_test_normalization", tags=["top-level-intermediate"]) }}
-- SQL model to prepare for deduplicating records based on the hash record column
select
  *,
  row_number() over (
    partition by _airbyte_dedup_exchange_rate_hashid
    order by _airbyte_emitted_at asc
  ) as _airbyte_row_num
from {{ ref('dedup_exchange_rate_ab3') }}
-- dedup_exchange_rate from {{ source('test_normalization', '_airbyte_raw_dedup_exchange_rate') }}

