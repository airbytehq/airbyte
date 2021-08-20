{{ config(schema="SYSTEM", tags=["nested-intermediate"]) }}
-- SQL model to build a hash column based on the values of this record
select
    ora_hash(
        'AIRBYTE_PARTITION_HASHID' || '~' ||
        'CURRENCY'
    ) as AIRBYTE_DATA_HASHID,
    tmp.*
from {{ ref('NESTED_STREAM_WITH_COMPLEX_COLUMNS_RESULTING_INTO_LONG_NAMES_PARTITION_DATA_AB2') }} tmp
-- DATA at nested_stream_with_complex_columns_resulting_into_long_names/partition/DATA

