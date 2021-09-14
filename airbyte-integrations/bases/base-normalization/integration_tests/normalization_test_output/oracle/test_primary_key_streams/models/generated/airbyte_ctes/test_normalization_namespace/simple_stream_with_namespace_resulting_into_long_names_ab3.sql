{{ config(schema="test_normalization", tags=["top-level-intermediate"]) }}
-- SQL model to build a hash column based on the values of this record
select
    {{ dbt_utils.surrogate_key([
        'id',
        quote('DATE'),
    ]) }} as {{ quote('_AIRBYTE_SIMPLE_STREAM_WITH_NAMESPACE_RESULTING_INTO_LONG_NAMES_HASHID') }},
    tmp.*
from {{ ref('simple_stream_with_namespace_resulting_into_long_names_ab2') }} tmp
-- simple_stream_with_namespace_resulting_into_long_names

