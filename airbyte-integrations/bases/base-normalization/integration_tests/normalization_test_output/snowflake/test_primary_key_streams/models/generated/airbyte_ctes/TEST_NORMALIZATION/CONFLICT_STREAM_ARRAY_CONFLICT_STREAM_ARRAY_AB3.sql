{{ config(schema="_AIRBYTE_TEST_NORMALIZATION", tags=["nested-intermediate"]) }}
-- SQL model to build a hash column based on the values of this record
select
    *,
    {{ dbt_utils.surrogate_key([
        '_AIRBYTE_CONFLICT_STREAM_ARRAY_HASHID',
        array_to_string('CONFLICT_STREAM_NAME'),
    ]) }} as _AIRBYTE_CONFLICT_STREAM_ARRAY_2_HASHID
from {{ ref('CONFLICT_STREAM_ARRAY_CONFLICT_STREAM_ARRAY_AB2') }}
-- CONFLICT_STREAM_ARRAY at conflict_stream_array/conflict_stream_array

