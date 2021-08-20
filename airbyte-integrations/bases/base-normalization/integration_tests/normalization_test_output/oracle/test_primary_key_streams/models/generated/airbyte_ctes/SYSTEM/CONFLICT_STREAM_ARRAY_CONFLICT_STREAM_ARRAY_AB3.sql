{{ config(schema="SYSTEM", tags=["nested-intermediate"]) }}
-- SQL model to build a hash column based on the values of this record
select
    ora_hash(
        'AIRBYTE_CONFLICT_STREAM_ARRAY_HASHID' || '~' ||
        {{array_to_string('CONFLICT_STREAM_NAME')}}
    ) as AIRBYTE_CONFLICT_STREAM_ARRAY_2_HASHID,
    tmp.*
from {{ ref('CONFLICT_STREAM_ARRAY_CONFLICT_STREAM_ARRAY_AB2') }} tmp
-- CONFLICT_STREAM_ARRAY at conflict_stream_array/conflict_stream_array

