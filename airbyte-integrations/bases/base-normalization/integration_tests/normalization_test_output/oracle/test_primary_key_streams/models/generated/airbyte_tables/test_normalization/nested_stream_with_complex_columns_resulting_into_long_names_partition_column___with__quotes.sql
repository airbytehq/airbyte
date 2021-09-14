{{ config(schema="test_normalization", tags=["nested"]) }}
-- Final base SQL model
select
    {{ quote('_AIRBYTE_PARTITION_HASHID') }},
    currency,
    {{ quote('_AIRBYTE_EMITTED_AT') }},
    {{ quote('_AIRBYTE_COLUMN___WITH__QUOTES_HASHID') }}
from {{ ref('nested_stream_with_complex_columns_resulting_into_long_names_partition_column___with__quotes_ab3') }}
-- column___with__quotes at nested_stream_with_complex_columns_resulting_into_long_names/partition/column`_'with"_quotes from {{ ref('nested_stream_with_complex_columns_resulting_into_long_names_partition') }}

