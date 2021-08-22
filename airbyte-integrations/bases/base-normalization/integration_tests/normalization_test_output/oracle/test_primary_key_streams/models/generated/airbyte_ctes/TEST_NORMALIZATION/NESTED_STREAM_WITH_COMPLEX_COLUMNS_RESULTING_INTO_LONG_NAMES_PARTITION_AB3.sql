{{ config(schema="TEST_NORMALIZATION", tags=["nested-intermediate"]) }}
-- SQL model to build a hash column based on the values of this record
select
    ora_hash(
        '{{ QUOTE('_AIRBYTE_NESTED_STREAM_WITH_COMPLEX_COLUMNS_RESULTING_INTO_LONG_NAMES_HASHID') }}' || '~' ||
        {{array_to_string('DOUBLE_ARRAY_DATA')}} || '~' ||
        {{array_to_string('DATA')}} || '~' ||
        {{array_to_string('COLUMN___WITH__QUOTES')}}
    ) as {{ QUOTE('_AIRBYTE_PARTITION_HASHID') }},
    tmp.*
from {{ ref('NESTED_STREAM_WITH_COMPLEX_COLUMNS_RESULTING_INTO_LONG_NAMES_PARTITION_AB2') }} tmp
-- PARTITION at nested_stream_with_complex_columns_resulting_into_long_names/partition

