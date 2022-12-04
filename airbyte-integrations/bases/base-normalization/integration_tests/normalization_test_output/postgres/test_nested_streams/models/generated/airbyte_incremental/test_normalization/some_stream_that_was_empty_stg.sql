{{ config(
    indexes = [{'columns':['_airbyte_emitted_at'],'type':'btree'}],
    unique_key = '_airbyte_ab_id',
    schema = "_airbyte_test_normalization",
    tags = [ "top-level-intermediate" ]
) }}
-- SQL model to build a hash column based on the values of this record
-- depends_on: {{ ref('some_stream_that_was_empty_ab2') }}
select
    {{ dbt_utils.surrogate_key([
        adapter.quote('id'),
        adapter.quote('date'),
    ]) }} as _airbyte_some_stream_that_was_empty_hashid,
    tmp.*
from {{ ref('some_stream_that_was_empty_ab2') }} tmp
-- some_stream_that_was_empty
where 1 = 1
{{ incremental_clause('_airbyte_emitted_at', this) }}

