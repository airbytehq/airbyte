{{ config(
    cluster_by = ["_AIRBYTE_EMITTED_AT"],
    unique_key = '_AIRBYTE_AB_ID',
    schema = "_AIRBYTE_TEST_NORMALIZATION",
    tags = [ "top-level-intermediate" ]
) }}
-- depends_on: ref('DEDUP_EXCHANGE_RATE_STG')
{% if is_incremental() %}
-- retrieve incremental "new" data
select
    *
from {{ ref('DEDUP_EXCHANGE_RATE_STG')  }}
-- DEDUP_EXCHANGE_RATE from {{ source('TEST_NORMALIZATION', '_AIRBYTE_RAW_DEDUP_EXCHANGE_RATE') }}
where 1 = 1
{{ incremental_clause('_AIRBYTE_EMITTED_AT', this) }}
{% else %}
select * from {{ ref('DEDUP_EXCHANGE_RATE_STG')  }}
{% endif %}
{{ incremental_clause('_AIRBYTE_EMITTED_AT', this) }}

