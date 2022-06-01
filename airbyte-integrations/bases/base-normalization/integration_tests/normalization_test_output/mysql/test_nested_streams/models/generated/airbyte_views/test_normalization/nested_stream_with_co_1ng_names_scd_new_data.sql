{{ config(
    unique_key = '_airbyte_ab_id',
    schema = "_airbyte_test_normalization",
    tags = [ "top-level-intermediate" ]
) }}
-- depends_on: ref('nested_stream_with_co_1g_into_long_names_stg')
{% if is_incremental() %}
-- retrieve incremental "new" data
select
    *
from {{ ref('nested_stream_with_co_1g_into_long_names_stg')  }}
-- nested_stream_with_co__lting_into_long_names from {{ source('test_normalization', '_airbyte_raw_nested_s__lting_into_long_names') }}
where 1 = 1
{{ incremental_clause('_airbyte_emitted_at', this) }}
{% else %}
select * from {{ ref('nested_stream_with_co_1g_into_long_names_stg')  }}
{% endif %}
{{ incremental_clause('_airbyte_emitted_at', this) }}

