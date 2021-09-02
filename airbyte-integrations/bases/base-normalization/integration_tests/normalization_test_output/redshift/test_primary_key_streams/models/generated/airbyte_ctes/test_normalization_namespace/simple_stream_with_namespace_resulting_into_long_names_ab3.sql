{{ config(schema="_airbyte_test_normalization_namespace", tags=["top-level-intermediate"]) }}
-- SQL model to build a hash column based on the values of this record
select
    *,
    {{ dbt_utils.surrogate_key([
        'id',
        'date',
    ]) }} as _airbyte_simple_stream_with_namespace_resulting_into_long_names_hashid
from {{ ref('simple_stream_with_namespace_resulting_into_long_names_ab2') }}
-- simple_stream_with_namespace_resulting_into_long_names

