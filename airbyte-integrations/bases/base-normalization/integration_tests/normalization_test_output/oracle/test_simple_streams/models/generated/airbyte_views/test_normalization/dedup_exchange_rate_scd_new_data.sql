{{ config(
    unique_key = quote('_AIRBYTE_AB_ID'),
    schema = "test_normalization",
    tags = [ "top-level-intermediate" ]
) }}
-- depends_on: ref('dedup_exchange_rate_stg')
{% if is_incremental() %}
-- retrieve incremental "new" data
select
    *
from {{ ref('dedup_exchange_rate_stg')  }}
-- dedup_exchange_rate from {{ source('test_normalization', 'airbyte_raw_dedup_exchange_rate') }}
where 1 = 1
{{ incremental_clause(quote('_AIRBYTE_EMITTED_AT'), this) }}
{% else %}
select * from {{ ref('dedup_exchange_rate_stg')  }}
{% endif %}
{{ incremental_clause(quote('_AIRBYTE_EMITTED_AT'), this) }}

