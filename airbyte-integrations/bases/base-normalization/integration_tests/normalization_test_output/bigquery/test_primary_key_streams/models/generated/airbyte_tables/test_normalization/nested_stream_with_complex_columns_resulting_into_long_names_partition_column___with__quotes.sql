{{ config(schema="test_normalization", tags=["nested"]) }}
-- Final base SQL model
select
    _airbyte_partition_hashid,
    currency,
    _airbyte_emitted_at,
    _airbyte_column___with__quotes_hashid
from {{ ref('nested_stream_with_complex_columns_resulting_into_long_names_partition_column___with__quotes_ab3') }}
-- column___with__quotes at nested_stream_with_complex_columns_resulting_into_long_names/partition/column`_'with"_quotes from {{ ref('nested_stream_with_complex_columns_resulting_into_long_names_partition') }}

