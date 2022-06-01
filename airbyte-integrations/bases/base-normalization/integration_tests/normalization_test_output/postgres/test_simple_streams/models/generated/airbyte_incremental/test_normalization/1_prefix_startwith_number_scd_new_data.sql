{{ config(
    indexes = [{'columns':['_airbyte_emitted_at'],'type':'btree'}],
    unique_key = '_airbyte_ab_id',
    schema = "_airbyte_test_normalization",
    tags = [ "top-level-intermediate" ]
) }}
-- depends_on: ref('1_prefix_startwith_number_stg')
{% if is_incremental() %}
-- retrieve incremental "new" data
select
    *
from {{ ref('1_prefix_startwith_number_stg')  }}
-- 1_prefix_startwith_number from {{ source('test_normalization', '_airbyte_raw_1_prefix_startwith_number') }}
where 1 = 1
{{ incremental_clause('_airbyte_emitted_at', this) }}
{% else %}
select * from {{ ref('1_prefix_startwith_number_stg')  }}
{% endif %}
{{ incremental_clause('_airbyte_emitted_at', this) }}

