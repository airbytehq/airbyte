{{ config(alias="nested_stream_with_complex_columns_resulting_into_long_names_64a_partition_ab3", schema="_airbyte_test_normalization", tags=["nested-intermediate"]) }}
-- SQL model to build a hash column based on the values of this record
select
    *,
    {{ dbt_utils.surrogate_key([
        '_airbyte_nested_stream_with_complex_columns_resulting_into_long_names_hashid',
        array_to_string('double_array_data'),
        array_to_string('DATA'),
    ]) }} as _airbyte_partition_hashid
from {{ ref('nested_stream_with_complex_columns_resulting_into_long_names_64a_partition_ab2_db2') }}
-- partition at nested_stream_with_complex_columns_resulting_into_long_names/partition

