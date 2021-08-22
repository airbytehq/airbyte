{{ config(schema="TEST_NORMALIZATION", tags=["nested-intermediate"]) }}
-- SQL model to build a hash column based on the values of this record
select
    ora_hash(
        '{{ QUOTE('_AIRBYTE_CONFLICT_STREAM_NAME_HASHID') }}' || '~' ||
        'CONFLICT_STREAM_NAME'
    ) as {{ QUOTE('_AIRBYTE_CONFLICT_STREAM_NAME_2_HASHID') }},
    tmp.*
from {{ ref('CONFLICT_STREAM_NAME_CONFLICT_STREAM_NAME_AB2') }} tmp
-- CONFLICT_STREAM_NAME at conflict_stream_name/conflict_stream_name

