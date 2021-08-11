{{ config(schema="_airbyte_test_normalization", tags=["top-level-intermediate"]) }}
-- SQL model to build a hash column based on the values of this record
select
    *,
    {{ dbt_utils.surrogate_key([
        adapter.quote('id'),
        'conflict_stream_array',
    ]) }} as _airbyte_conflict_stream_array_hashid
from {{ ref('conflict_stream_array_ab2') }}
-- conflict_stream_array

