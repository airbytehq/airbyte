{{ config(schema="test_normalization", tags=["nested-intermediate"]) }}
-- SQL model to build a hash column based on the values of this record
select
    {{ dbt_utils.surrogate_key([
        quote('_AIRBYTE_CONFLICT_STREAM_NAME_HASHID'),
        'conflict_stream_name',
    ]) }} as {{ quote('_AIRBYTE_CONFLICT_STREAM_NAME_2_HASHID') }},
    tmp.*
from {{ ref('conflict_stream_name_conflict_stream_name_ab2') }} tmp
-- conflict_stream_name at conflict_stream_name/conflict_stream_name

