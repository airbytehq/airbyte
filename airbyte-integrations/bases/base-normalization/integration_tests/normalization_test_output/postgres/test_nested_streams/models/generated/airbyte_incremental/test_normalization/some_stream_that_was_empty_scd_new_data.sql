{{ config(
    indexes = [{'columns':['_airbyte_emitted_at'],'type':'btree'}],
    unique_key = '_airbyte_ab_id',
    schema = "_airbyte_test_normalization",
    tags = [ "top-level-intermediate" ]
) }}
-- depends_on: ref('some_stream_that_was_empty_stg')
{% if is_incremental() %}
-- retrieve incremental "new" data
select
    *
from {{ ref('some_stream_that_was_empty_stg')  }}
-- some_stream_that_was_empty from {{ source('test_normalization', '_airbyte_raw_some_stream_that_was_empty') }}
where 1 = 1
{{ incremental_clause('_airbyte_emitted_at', this) }}
{% else %}
select * from {{ ref('some_stream_that_was_empty_stg')  }}
{% endif %}
{{ incremental_clause('_airbyte_emitted_at', this) }}

