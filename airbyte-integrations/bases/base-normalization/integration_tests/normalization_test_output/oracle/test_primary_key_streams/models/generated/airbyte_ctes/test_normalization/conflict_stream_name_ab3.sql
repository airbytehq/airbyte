{{ config(schema="test_normalization", tags=["top-level-intermediate"]) }}
-- SQL model to build a hash column based on the values of this record
select
    ora_hash(
        'id' || '~' ||
        'conflict_stream_name'
    ) as {{ QUOTE('_AIRBYTE_CONFLICT_STREAM_NAME_HASHID') }},
    tmp.*
from {{ ref('conflict_stream_name_ab2') }} tmp
-- conflict_stream_name

