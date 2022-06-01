{{ config(
    sort = "_airbyte_emitted_at",
    unique_key = '_airbyte_ab_id',
    schema = "_airbyte_test_normalization",
    tags = [ "top-level-intermediate" ]
) }}
-- depends_on: ref('dedup_exchange_rate_stg')
{% if is_incremental() %}
-- retrieve incremental "new" data
select
    *
from {{ ref('dedup_exchange_rate_stg')  }}
-- dedup_exchange_rate from {{ source('test_normalization', '_airbyte_raw_dedup_exchange_rate') }}
where 1 = 1
{{ incremental_clause('_airbyte_emitted_at', this) }}
{% else %}
select * from {{ ref('dedup_exchange_rate_stg')  }}
{% endif %}
{{ incremental_clause('_airbyte_emitted_at', this) }}

