{{ config(schema="TEST_NORMALIZATION", tags=["nested-intermediate"]) }}
-- SQL model to build a hash column based on the values of this record
select
    ora_hash(
        '{{ QUOTE('_AIRBYTE_PARTITION_HASHID') }}' || '~' ||
        'ID'
    ) as {{ QUOTE('_AIRBYTE_DOUBLE_ARRAY_DATA_HASHID') }},
    tmp.*
from {{ ref('NESTED_STREAM_WITH_COMPLEX_COLUMNS_RESULTING_INTO_LONG_NAMES_PARTITION_DOUBLE_ARRAY_DATA_AB2') }} tmp
-- DOUBLE_ARRAY_DATA at nested_stream_with_complex_columns_resulting_into_long_names/partition/double_array_data

