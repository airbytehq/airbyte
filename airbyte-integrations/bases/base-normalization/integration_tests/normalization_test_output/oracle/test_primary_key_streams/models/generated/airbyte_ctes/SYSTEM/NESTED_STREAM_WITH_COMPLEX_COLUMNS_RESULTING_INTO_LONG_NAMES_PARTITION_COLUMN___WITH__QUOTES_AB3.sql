{{ config(schema="SYSTEM", tags=["nested-intermediate"]) }}
-- SQL model to build a hash column based on the values of this record
select
    ora_hash(
        'AIRBYTE_PARTITION_HASHID' || '~' ||
        'CURRENCY'
    ) as AIRBYTE_COLUMN___WITH__QUOTES_HASHID,
    tmp.*
from {{ ref('NESTED_STREAM_WITH_COMPLEX_COLUMNS_RESULTING_INTO_LONG_NAMES_PARTITION_COLUMN___WITH__QUOTES_AB2') }} tmp
-- COLUMN___WITH__QUOTES at nested_stream_with_complex_columns_resulting_into_long_names/partition/column`_'with"_quotes

