{{ config(
    indexes = [{'columns':['_airbyte_emitted_at'],'type':'btree'}],
    unique_key = '_airbyte_ab_id',
    schema = "_airbyte_test_normalization",
    tags = [ "top-level-intermediate" ]
) }}
-- depends_on: ref('renamed_dedup_cdc_excluded_stg')
{% if is_incremental() %}
-- retrieve incremental "new" data
select
    *
from {{ ref('renamed_dedup_cdc_excluded_stg')  }}
-- renamed_dedup_cdc_excluded from {{ source('test_normalization', '_airbyte_raw_renamed_dedup_cdc_excluded') }}
where 1 = 1
{{ incremental_clause('_airbyte_emitted_at', this) }}
{% else %}
select * from {{ ref('renamed_dedup_cdc_excluded_stg')  }}
{% endif %}
{{ incremental_clause('_airbyte_emitted_at', this) }}

