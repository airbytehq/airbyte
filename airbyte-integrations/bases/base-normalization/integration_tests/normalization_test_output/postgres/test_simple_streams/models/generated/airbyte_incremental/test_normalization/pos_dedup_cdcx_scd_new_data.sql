{{ config(
    indexes = [{'columns':['_airbyte_emitted_at'],'type':'btree'}],
    unique_key = '_airbyte_ab_id',
    schema = "_airbyte_test_normalization",
    tags = [ "top-level-intermediate" ]
) }}
-- depends_on: ref('pos_dedup_cdcx_stg')
{% if is_incremental() %}
-- retrieve incremental "new" data
select
    *
from {{ ref('pos_dedup_cdcx_stg')  }}
-- pos_dedup_cdcx from {{ source('test_normalization', '_airbyte_raw_pos_dedup_cdcx') }}
where 1 = 1
{{ incremental_clause('_airbyte_emitted_at', this) }}
{% else %}
select * from {{ ref('pos_dedup_cdcx_stg')  }}
{% endif %}
{{ incremental_clause('_airbyte_emitted_at', this) }}

