{{ config(schema="test_normalization", tags=["nested-intermediate"]) }}
-- SQL model to build a hash column based on the values of this record
select
    {{ dbt_utils.surrogate_key([
        quote('_AIRBYTE_PARTITION_HASHID'),
        'currency',
    ]) }} as {{ quote('_AIRBYTE_COLUMN___WITH__QUOTES_HASHID') }},
    tmp.*
from {{ ref('nested_stream_with_complex_columns_resulting_into_long_names_partition_column___with__quotes_ab2') }} tmp
-- column___with__quotes at nested_stream_with_complex_columns_resulting_into_long_names/partition/column`_'with"_quotes

