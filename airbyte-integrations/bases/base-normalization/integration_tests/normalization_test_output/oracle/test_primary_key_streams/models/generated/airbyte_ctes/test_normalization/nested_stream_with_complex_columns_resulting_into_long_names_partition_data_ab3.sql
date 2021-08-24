{{ config(schema="test_normalization", tags=["nested-intermediate"]) }}
-- SQL model to build a hash column based on the values of this record
select
    ora_hash(
        '{{ QUOTE('_AIRBYTE_PARTITION_HASHID') }}' || '~' ||
        'currency'
    ) as {{ QUOTE('_AIRBYTE_DATA_HASHID') }},
    tmp.*
from {{ ref('nested_stream_with_complex_columns_resulting_into_long_names_partition_data_ab2') }} tmp
-- data at nested_stream_with_complex_columns_resulting_into_long_names/partition/DATA

