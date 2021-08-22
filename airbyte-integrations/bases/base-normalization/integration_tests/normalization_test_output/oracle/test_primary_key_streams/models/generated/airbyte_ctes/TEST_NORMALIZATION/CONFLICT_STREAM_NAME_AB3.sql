{{ config(schema="TEST_NORMALIZATION", tags=["top-level-intermediate"]) }}
-- SQL model to build a hash column based on the values of this record
select
    ora_hash(
        'ID' || '~' ||
        'CONFLICT_STREAM_NAME'
    ) as {{ QUOTE('_AIRBYTE_CONFLICT_STREAM_NAME_HASHID') }},
    tmp.*
from {{ ref('CONFLICT_STREAM_NAME_AB2') }} tmp
-- CONFLICT_STREAM_NAME

