{{ config(schema="test_normalization", tags=["top-level-intermediate"]) }}
-- SQL model to build a hash column based on the values of this record
select
    {{ dbt_utils.surrogate_key([
        'id',
        quote('DATE'),
        'partition',
    ]) }} as {{ quote('_AIRBYTE_NESTED_STREAM_WITH_COMPLEX_COLUMNS_RESULTING_INTO_LONG_NAMES_HASHID') }},
    tmp.*
from {{ ref('nested_stream_with_complex_columns_resulting_into_long_names_ab2') }} tmp
-- nested_stream_with_complex_columns_resulting_into_long_names

