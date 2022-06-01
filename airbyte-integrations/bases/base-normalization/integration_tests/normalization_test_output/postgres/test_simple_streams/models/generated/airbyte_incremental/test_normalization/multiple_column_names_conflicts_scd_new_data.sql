{{ config(
    indexes = [{'columns':['_airbyte_emitted_at'],'type':'btree'}],
    unique_key = '_airbyte_ab_id',
    schema = "_airbyte_test_normalization",
    tags = [ "top-level-intermediate" ]
) }}
-- depends_on: ref('multiple_column_names_conflicts_stg')
{% if is_incremental() %}
-- retrieve incremental "new" data
select
    *
from {{ ref('multiple_column_names_conflicts_stg')  }}
-- multiple_column_names_conflicts from {{ source('test_normalization', '_airbyte_raw_multiple_column_names_conflicts') }}
where 1 = 1
{{ incremental_clause('_airbyte_emitted_at', this) }}
{% else %}
select * from {{ ref('multiple_column_names_conflicts_stg')  }}
{% endif %}
{{ incremental_clause('_airbyte_emitted_at', this) }}

