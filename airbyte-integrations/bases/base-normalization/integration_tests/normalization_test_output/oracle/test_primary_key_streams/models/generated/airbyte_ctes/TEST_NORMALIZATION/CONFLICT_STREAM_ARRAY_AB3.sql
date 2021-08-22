{{ config(schema="TEST_NORMALIZATION", tags=["top-level-intermediate"]) }}
-- SQL model to build a hash column based on the values of this record
select
    ora_hash(
        'ID' || '~' ||
        {{array_to_string('CONFLICT_STREAM_ARRAY')}}
    ) as {{ QUOTE('_AIRBYTE_CONFLICT_STREAM_ARRAY_HASHID') }},
    tmp.*
from {{ ref('CONFLICT_STREAM_ARRAY_AB2') }} tmp
-- CONFLICT_STREAM_ARRAY

