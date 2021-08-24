{{ config(schema="test_normalization", tags=["top-level-intermediate"]) }}
-- SQL model to build a hash column based on the values of this record
select
    ora_hash(
        'id' || '~' ||
        {{array_to_string('conflict_stream_array')}}
    ) as {{ QUOTE('_AIRBYTE_CONFLICT_STREAM_ARRAY_HASHID') }},
    tmp.*
from {{ ref('conflict_stream_array_ab2') }} tmp
-- conflict_stream_array

