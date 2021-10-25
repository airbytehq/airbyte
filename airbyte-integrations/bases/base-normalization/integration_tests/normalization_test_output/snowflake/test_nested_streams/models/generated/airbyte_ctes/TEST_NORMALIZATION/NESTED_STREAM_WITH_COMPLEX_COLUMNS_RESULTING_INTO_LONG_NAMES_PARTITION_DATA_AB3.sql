{{ config(schema="_AIRBYTE_TEST_NORMALIZATION", tags=["nested-intermediate"]) }}
-- SQL model to build a hash column based on the values of this record
select
    {{ dbt_utils.surrogate_key([
        '_AIRBYTE_PARTITION_HASHID',
        'CURRENCY',
    ]) }} as _AIRBYTE_DATA_HASHID,
    tmp.*
from {{ ref('NESTED_STREAM_WITH_COMPLEX_COLUMNS_RESULTING_INTO_LONG_NAMES_PARTITION_DATA_AB2') }} tmp
-- DATA at nested_stream_with_complex_columns_resulting_into_long_names/partition/DATA

