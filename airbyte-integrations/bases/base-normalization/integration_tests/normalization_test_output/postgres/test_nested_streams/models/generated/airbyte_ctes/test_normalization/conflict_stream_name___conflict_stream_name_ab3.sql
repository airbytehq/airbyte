{{ config(
    indexes = [{'columns':['_airbyte_emitted_at'],'type':'btree'}],
    schema = "_airbyte_test_normalization",
    tags = [ "nested-intermediate" ]
) }}
-- SQL model to build a hash column based on the values of this record
-- depends_on: {{ ref('conflict_stream_name___conflict_stream_name_ab2') }}
select
    {{ dbt_utils.surrogate_key([
        '_airbyte_conflict_stream_name_2_hashid',
        'groups',
    ]) }} as _airbyte_conflict_stream_name_3_hashid,
    tmp.*
from {{ ref('conflict_stream_name___conflict_stream_name_ab2') }} tmp
-- conflict_stream_name at conflict_stream_name/conflict_stream_name/conflict_stream_name
where 1 = 1

