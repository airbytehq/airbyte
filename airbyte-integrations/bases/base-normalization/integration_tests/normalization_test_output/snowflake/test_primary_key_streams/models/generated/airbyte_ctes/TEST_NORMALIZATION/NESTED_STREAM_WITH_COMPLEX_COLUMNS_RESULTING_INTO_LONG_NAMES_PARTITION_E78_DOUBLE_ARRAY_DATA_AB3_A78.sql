{{ config(alias="NESTED_STREAM_WITH_COMPLEX_COLUMNS_RESULTING_INTO_LONG_NAMES_PARTITION_E78_DOUBLE_ARRAY_DATA_AB3", schema="_AIRBYTE_TEST_NORMALIZATION", tags=["nested-intermediate"]) }}
-- SQL model to build a hash column based on the values of this record
select
    *,
    {{ dbt_utils.surrogate_key([
        '_AIRBYTE_PARTITION_HASHID',
        'ID',
    ]) }} as _AIRBYTE_DOUBLE_ARRAY_DATA_HASHID
from {{ ref('NESTED_STREAM_WITH_COMPLEX_COLUMNS_RESULTING_INTO_LONG_NAMES_PARTITION_E78_DOUBLE_ARRAY_DATA_AB2_A78') }}
-- DOUBLE_ARRAY_DATA at nested_stream_with_complex_columns_resulting_into_long_names/partition/double_array_data

