{{ config(schema="SYSTEM", tags=["nested-intermediate"]) }}
-- SQL model to build a hash column based on the values of this record
select
    ora_hash(
        'AIRBYTE_CONFLICT_STREAM_ARRAY_2_HASHID' || '~' ||
        'ID'
    ) as AIRBYTE_CONFLICT_STREAM_NAME_HASHID,
    tmp.*
from {{ ref('CONFLICT_STREAM_ARRAY_CONFLICT_STREAM_ARRAY_CONFLICT_STREAM_NAME_AB2') }} tmp
-- CONFLICT_STREAM_NAME at conflict_stream_array/conflict_stream_array/conflict_stream_name

