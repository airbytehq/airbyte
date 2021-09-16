{{ config(schema="test_normalization", tags=["top-level-intermediate"]) }}
-- SQL model to build a hash column based on the values of this record
select
    {{ dbt_utils.surrogate_key([
        'id',
        'conflict_stream_scalar',
    ]) }} as {{ quote('_AIRBYTE_CONFLICT_STREAM_SCALAR_HASHID') }},
    tmp.*
from {{ ref('conflict_stream_scalar_ab2') }} tmp
-- conflict_stream_scalar

