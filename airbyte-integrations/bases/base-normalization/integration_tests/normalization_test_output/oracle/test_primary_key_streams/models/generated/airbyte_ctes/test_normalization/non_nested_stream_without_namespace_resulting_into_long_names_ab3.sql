{{ config(schema="test_normalization", tags=["top-level-intermediate"]) }}
-- SQL model to build a hash column based on the values of this record
select
    {{ dbt_utils.surrogate_key([
        'id',
        quote('DATE'),
    ]) }} as {{ quote('_AIRBYTE_NON_NESTED_STREAM_WITHOUT_NAMESPACE_RESULTING_INTO_LONG_NAMES_HASHID') }},
    tmp.*
from {{ ref('non_nested_stream_without_namespace_resulting_into_long_names_ab2') }} tmp
-- non_nested_stream_without_namespace_resulting_into_long_names

