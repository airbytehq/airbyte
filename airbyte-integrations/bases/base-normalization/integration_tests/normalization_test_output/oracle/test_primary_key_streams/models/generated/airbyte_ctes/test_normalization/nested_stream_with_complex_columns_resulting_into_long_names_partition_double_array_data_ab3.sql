{{ config(schema="test_normalization", tags=["nested-intermediate"]) }}
-- SQL model to build a hash column based on the values of this record
select
    {{ dbt_utils.surrogate_key([
        quote('_AIRBYTE_PARTITION_HASHID'),
        'id',
    ]) }} as {{ quote('_AIRBYTE_DOUBLE_ARRAY_DATA_HASHID') }},
    tmp.*
from {{ ref('nested_stream_with_complex_columns_resulting_into_long_names_partition_double_array_data_ab2') }} tmp
-- double_array_data at nested_stream_with_complex_columns_resulting_into_long_names/partition/double_array_data

