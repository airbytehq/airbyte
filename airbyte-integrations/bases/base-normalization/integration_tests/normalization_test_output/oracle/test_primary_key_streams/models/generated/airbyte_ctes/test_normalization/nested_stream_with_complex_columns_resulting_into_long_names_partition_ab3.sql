{{ config(schema="test_normalization", tags=["nested-intermediate"]) }}
-- SQL model to build a hash column based on the values of this record
select
    {{ dbt_utils.surrogate_key([
        quote('_AIRBYTE_NESTED_STREAM_WITH_COMPLEX_COLUMNS_RESULTING_INTO_LONG_NAMES_HASHID'),
        array_to_string('double_array_data'),
        array_to_string('data'),
        array_to_string('column___with__quotes'),
    ]) }} as {{ quote('_AIRBYTE_PARTITION_HASHID') }},
    tmp.*
from {{ ref('nested_stream_with_complex_columns_resulting_into_long_names_partition_ab2') }} tmp
-- partition at nested_stream_with_complex_columns_resulting_into_long_names/partition

